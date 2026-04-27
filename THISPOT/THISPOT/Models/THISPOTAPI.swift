//
//  THISPOTAPI.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import Foundation
import UIKit

/// Backend client for ThiSpot. Currently wires only `/api/analyze-photo`;
/// other endpoints (login-demo, recommend-color, finish-walk, generation-jobs)
/// will be added when their flows are integrated.
enum ThiSpotAPI {
    /// Tunnel to local backend via ngrok. Replace when the tunnel restarts
    /// (free-tier URL changes every session) or when moving to a real host.
    static let baseURL = URL(string: "https://democracy-effort-reward.ngrok-free.dev")!

    /// Backend embeds absolute URLs like `http://localhost:8000/...` in
    /// responses, which the device cannot reach. Swap the host so we go
    /// through our configured baseURL (ngrok in dev, production host later).
    static func rewriteServerURL(_ raw: String) -> URL? {
        let prefixes = ["http://localhost:8000", "http://127.0.0.1:8000"]
        var s = raw
        for prefix in prefixes where s.hasPrefix(prefix) {
            s = baseURL.absoluteString + String(s.dropFirst(prefix.count))
            break
        }
        return URL(string: s)
    }

    // MARK: - Response types

    struct AnalyzeResponse: Decodable {
        let photo_id: String
        let proof_result: ProofResult
        let vision_result: VisionResult?
        let discovery_result: DiscoveryResult?
    }

    struct ProofResult: Decodable {
        let accepted: Bool
        let accepted_count: Int
        let required_count: Int
        let remaining_count: Int
        let completion_unlocked: Bool
    }

    struct VisionResult: Decodable {
        let detected_color: String?
        let match_score: Double?
        let is_matched: Bool?
        let object_label: String?
        let feedback: String?
    }

    struct DiscoveryResult: Decodable {
        let is_new_spot: Bool?
        let shared_user_percent: Int?
        let message: String?
    }

    struct RecommendRequest: Encodable {
        let user_id: String
        let previous_colors: [String]
    }

    struct RecommendResponse: Decodable {
        let target_color: String
        let mission_title: String?
        let mission_text: String?
        let character_outfit_color: String?
    }

    struct FinishWalkRequest: Encodable {
        let user_id: String
        let session_id: String
        let target_color: String
        let distance_m: Int
        let steps: Int
        let duration_sec: Int
        let photo_ids: [String]
        let best_match_score: Double
        let is_new_spot: Bool
    }

    struct FinishWalkResponse: Decodable {
        let badge: Badge?
        let final_result_url: String?
        let report: Report?
        let summary: Summary?

        struct Badge: Decodable {
            let title: String?
            let description: String?
            let rarity: String?
            let image_url: String?
        }

        struct Report: Decodable {
            let status: String
            let type: String
            let video_url: String?
            let image_url: String?
            let thumbnail_url: String?
            let share_media_url: String?
            let share_media_type: String?
            let can_share_to_instagram_story: Bool?
            let generation_job_id: String?
            let caption: String?
        }

        struct Summary: Decodable {
            let title: String?
            let subtitle: String?
            let spot_message: String?
            let share_caption: String?
        }
    }

    struct GenerationJobResponse: Decodable {
        let job_id: String
        let status: String  // queued | running | completed | fallback | failed
        let report: FinishWalkResponse.Report?
        let message: String?
    }

    // MARK: - Errors

    enum APIError: LocalizedError {
        case invalidImage
        case http(status: Int, body: String)
        case transport(Error)
        case decode(Error)

        var errorDescription: String? {
            switch self {
            case .invalidImage:           return "Couldn't prepare the photo."
            case .http(let s, let body):  return "Server (\(s)): \(body.prefix(120))"
            case .transport(let e):       return "Network: \(e.localizedDescription)"
            case .decode(let e):          return "Bad response: \(e.localizedDescription)"
            }
        }
    }

    // MARK: - Endpoints

    static func recommendColor(
        userID: String,
        previousColors: [String]
    ) async throws -> RecommendResponse {
        let url = baseURL.appendingPathComponent("api/recommend-color")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.timeoutInterval = 30
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        let payload = RecommendRequest(user_id: userID, previous_colors: previousColors)
        req.httpBody = try JSONEncoder().encode(payload)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.transport(error)
        }

        if let http = response as? HTTPURLResponse,
           !(200..<300).contains(http.statusCode) {
            let bodyStr = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http(status: http.statusCode, body: bodyStr)
        }

        do {
            return try JSONDecoder().decode(RecommendResponse.self, from: data)
        } catch {
            #if DEBUG
            print("[ThiSpotAPI] recommend decode failed:",
                  String(data: data, encoding: .utf8) ?? "<binary>")
            #endif
            throw APIError.decode(error)
        }
    }

    static func finishWalk(
        userID: String,
        sessionID: String,
        targetColor: String,
        distanceM: Int,
        steps: Int,
        durationSec: Int,
        photoIDs: [String],
        bestMatchScore: Double,
        isNewSpot: Bool
    ) async throws -> FinishWalkResponse {
        let url = baseURL.appendingPathComponent("api/finish-walk")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.timeoutInterval = 120 // report generation can take a while when synchronous
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        req.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        let payload = FinishWalkRequest(
            user_id: userID,
            session_id: sessionID,
            target_color: targetColor,
            distance_m: distanceM,
            steps: steps,
            duration_sec: durationSec,
            photo_ids: photoIDs,
            best_match_score: bestMatchScore,
            is_new_spot: isNewSpot
        )
        req.httpBody = try JSONEncoder().encode(payload)

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.transport(error)
        }

        if let http = response as? HTTPURLResponse,
           !(200..<300).contains(http.statusCode) {
            let bodyStr = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http(status: http.statusCode, body: bodyStr)
        }

        do {
            return try JSONDecoder().decode(FinishWalkResponse.self, from: data)
        } catch {
            #if DEBUG
            print("[ThiSpotAPI] finishWalk decode failed:",
                  String(data: data, encoding: .utf8) ?? "<binary>")
            #endif
            throw APIError.decode(error)
        }
    }

    static func getGenerationJob(jobID: String) async throws -> GenerationJobResponse {
        let url = baseURL.appendingPathComponent("api/generation-jobs/\(jobID)")
        var req = URLRequest(url: url)
        req.httpMethod = "GET"
        req.timeoutInterval = 30
        req.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.data(for: req)
        } catch {
            throw APIError.transport(error)
        }

        if let http = response as? HTTPURLResponse,
           !(200..<300).contains(http.statusCode) {
            let bodyStr = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http(status: http.statusCode, body: bodyStr)
        }

        do {
            return try JSONDecoder().decode(GenerationJobResponse.self, from: data)
        } catch {
            #if DEBUG
            print("[ThiSpotAPI] generation-jobs decode failed:",
                  String(data: data, encoding: .utf8) ?? "<binary>")
            #endif
            throw APIError.decode(error)
        }
    }

    static func analyzePhoto(
        image: UIImage,
        userID: String,
        sessionID: String,
        targetColor: String,
        lat: Double? = nil,
        lng: Double? = nil
    ) async throws -> AnalyzeResponse {
        guard let jpeg = image.jpegData(compressionQuality: 0.85) else {
            throw APIError.invalidImage
        }

        let url = baseURL.appendingPathComponent("api/analyze-photo")
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.timeoutInterval = 30

        let boundary = "Boundary-\(UUID().uuidString)"
        req.setValue("multipart/form-data; boundary=\(boundary)",
                     forHTTPHeaderField: "Content-Type")
        // Skip ngrok free-tier "Visit Site" interstitial page
        req.setValue("true", forHTTPHeaderField: "ngrok-skip-browser-warning")

        var body = Data()
        func appendField(_ name: String, _ value: String) {
            body.append("--\(boundary)\r\n")
            body.append("Content-Disposition: form-data; name=\"\(name)\"\r\n\r\n")
            body.append("\(value)\r\n")
        }
        appendField("user_id", userID)
        appendField("session_id", sessionID)
        appendField("target_color", targetColor)
        if let lat { appendField("lat", String(lat)) }
        if let lng { appendField("lng", String(lng)) }

        body.append("--\(boundary)\r\n")
        body.append("Content-Disposition: form-data; name=\"photo\"; filename=\"photo.jpg\"\r\n")
        body.append("Content-Type: image/jpeg\r\n\r\n")
        body.append(jpeg)
        body.append("\r\n")
        body.append("--\(boundary)--\r\n")

        let data: Data
        let response: URLResponse
        do {
            (data, response) = try await URLSession.shared.upload(for: req, from: body)
        } catch {
            throw APIError.transport(error)
        }

        if let http = response as? HTTPURLResponse,
           !(200..<300).contains(http.statusCode) {
            let bodyStr = String(data: data, encoding: .utf8) ?? ""
            throw APIError.http(status: http.statusCode, body: bodyStr)
        }

        do {
            return try JSONDecoder().decode(AnalyzeResponse.self, from: data)
        } catch {
            #if DEBUG
            print("[ThiSpotAPI] decode failed. Body:",
                  String(data: data, encoding: .utf8) ?? "<binary>")
            #endif
            throw APIError.decode(error)
        }
    }
}

// Convenience for building multipart bodies
private extension Data {
    mutating func append(_ string: String) {
        if let d = string.data(using: .utf8) { append(d) }
    }
}
