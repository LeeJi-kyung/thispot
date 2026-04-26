//
//  RecordsView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct RecordsView: View {
    @Environment(\.dismiss) private var dismiss

    @State private var photoURLs: [URL] = []
    @State private var selectedPhoto: PhotoSelection? = nil

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)
    private let placeholderGray = Color(red: 0.70, green: 0.70, blue: 0.70)

    private let columns = [
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10),
        GridItem(.flexible(), spacing: 10)
    ]

    var body: some View {
        ZStack {
            backgroundCream.ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {

                // MARK: - Custom Back Button
                Button {
                    dismiss()
                } label: {
                    Image(systemName: "chevron.left")
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(brandBrown)
                        .frame(width: 40, height: 40)
                        .background(Circle().fill(Color.white.opacity(0.7)))
                        .overlay(Circle().stroke(brandBrown.opacity(0.15), lineWidth: 1))
                }
                .padding(.top, 8)
                .padding(.horizontal, 20)

                // MARK: - Title
                Text("Records")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(textDark)
                    .padding(.top, 24)
                    .padding(.horizontal, 28)

                Text(photoURLs.isEmpty
                     ? "Snap your first color find on a walk."
                     : "\(photoURLs.count) color \(photoURLs.count == 1 ? "moment" : "moments") collected.")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(brandBrown.opacity(0.85))
                    .padding(.top, 8)
                    .padding(.horizontal, 28)

                Spacer().frame(height: 20)

                // MARK: - Grid or empty state
                if photoURLs.isEmpty {
                    emptyState
                } else {
                    photoGrid
                }
            }
        }
        .navigationBarBackButtonHidden(true)
        .onAppear {
            photoURLs = WalkPhotoStore.loadAllPhotoURLs()
        }
        .fullScreenCover(item: $selectedPhoto) { selection in
            if let img = UIImage(contentsOfFile: photoURLs[selection.index].path) {
                PhotoViewer(image: img)
            }
        }
    }

    private var photoGrid: some View {
        ScrollView {
            LazyVGrid(columns: columns, spacing: 10) {
                ForEach(Array(photoURLs.enumerated()), id: \.element) { idx, url in
                    Button {
                        selectedPhoto = PhotoSelection(index: idx)
                    } label: {
                        thumbnail(for: url)
                    }
                    .buttonStyle(PressableScaleStyle())
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 32)
        }
    }

    private func thumbnail(for url: URL) -> some View {
        Group {
            if let img = UIImage(contentsOfFile: url.path) {
                Image(uiImage: img)
                    .resizable()
                    .scaledToFill()
            } else {
                Rectangle().fill(placeholderGray.opacity(0.3))
            }
        }
        .frame(height: 110)
        .clipped()
        .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
        .overlay(
            RoundedRectangle(cornerRadius: 14, style: .continuous)
                .stroke(Color.white, lineWidth: 2)
        )
        .shadow(color: brandBrown.opacity(0.18), radius: 5, x: 0, y: 2)
    }

    private var emptyState: some View {
        VStack(spacing: 14) {
            Spacer()
            Image(systemName: "photo.on.rectangle.angled")
                .font(.system(size: 48, weight: .light))
                .foregroundColor(brandBrown.opacity(0.45))
            Text("No records yet")
                .font(.system(size: 15, weight: .semibold))
                .foregroundColor(brandBrown.opacity(0.8))
            Text("Photos you take during walks\nwill show up here.")
                .font(.system(size: 13))
                .foregroundColor(brandBrown.opacity(0.6))
                .multilineTextAlignment(.center)
            Spacer()
            Spacer()
        }
        .frame(maxWidth: .infinity)
    }
}

#Preview {
    RecordsView()
}
