//
//  WalkPhotoStore.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import UIKit

/// Saves walk photos inside the app's sandbox (`Documents/Walks/{walkID}/`).
/// Photos stay private to THISPOT — we don't write to the system Photos library.
enum WalkPhotoStore {
    static var documentsURL: URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
    }

    static func walkDirectory(for walkID: String) -> URL {
        let url = documentsURL
            .appendingPathComponent("Walks", isDirectory: true)
            .appendingPathComponent(walkID, isDirectory: true)
        try? FileManager.default.createDirectory(
            at: url,
            withIntermediateDirectories: true
        )
        return url
    }

    @discardableResult
    static func save(_ image: UIImage, walkID: String) -> URL? {
        guard let data = image.jpegData(compressionQuality: 0.85) else { return nil }
        let fileURL = walkDirectory(for: walkID)
            .appendingPathComponent("\(UUID().uuidString).jpg")
        do {
            try data.write(to: fileURL, options: .atomic)
            return fileURL
        } catch {
            return nil
        }
    }

    /// Downloads a server-generated report image and stores it alongside the
    /// walk's photos. Filename starts with `report_` so it can be visually
    /// distinguished later if needed. Returns the local file URL.
    static func saveRemoteReport(from url: URL, walkID: String) async -> URL? {
        var req = URLRequest(url: url)
        req.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        do {
            let (data, response) = try await URLSession.shared.data(for: req)
            if let http = response as? HTTPURLResponse,
               !(200..<300).contains(http.statusCode) {
                return nil
            }

            // Pick extension from Content-Type, falling back to URL path.
            let ext: String = {
                if let http = response as? HTTPURLResponse,
                   let mime = http.value(forHTTPHeaderField: "Content-Type")?.lowercased() {
                    if mime.contains("png")  { return "png" }
                    if mime.contains("webp") { return "webp" }
                    if mime.contains("jpeg") || mime.contains("jpg") { return "jpg" }
                }
                let pathExt = url.pathExtension.lowercased()
                return pathExt.isEmpty ? "jpg" : pathExt
            }()

            let fileURL = walkDirectory(for: walkID)
                .appendingPathComponent("report_\(UUID().uuidString).\(ext)")
            try data.write(to: fileURL, options: .atomic)
            return fileURL
        } catch {
            #if DEBUG
            print("[WalkPhotoStore] saveRemoteReport failed:", error)
            #endif
            return nil
        }
    }

    /// Returns every saved photo URL across all walks, newest first.
    static func loadAllPhotoURLs() -> [URL] {
        let walksRoot = documentsURL.appendingPathComponent("Walks", isDirectory: true)
        let fm = FileManager.default
        guard let walkFolders = try? fm.contentsOfDirectory(
            at: walksRoot,
            includingPropertiesForKeys: [.contentModificationDateKey],
            options: [.skipsHiddenFiles]
        ) else { return [] }

        var photos: [URL] = []
        for folder in walkFolders {
            guard let files = try? fm.contentsOfDirectory(
                at: folder,
                includingPropertiesForKeys: [.contentModificationDateKey],
                options: [.skipsHiddenFiles]
            ) else { continue }
            let allowed: Set<String> = ["jpg", "jpeg", "png", "webp"]
            photos.append(contentsOf: files.filter { allowed.contains($0.pathExtension.lowercased()) })
        }

        return photos.sorted { lhs, rhs in
            let l = (try? lhs.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
            let r = (try? rhs.resourceValues(forKeys: [.contentModificationDateKey]).contentModificationDate) ?? .distantPast
            return l > r
        }
    }
}
