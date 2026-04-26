//
//  PotGalleryView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

/// Swipeable full-screen viewer for everything currently in the POT.
struct PotGalleryView: View {
    let photos: [UIImage]
    let color: WalkColor

    @Environment(\.dismiss) private var dismiss
    @State private var currentIndex = 0

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            TabView(selection: $currentIndex) {
                ForEach(Array(photos.enumerated()), id: \.offset) { idx, img in
                    Image(uiImage: img)
                        .resizable()
                        .scaledToFit()
                        .ignoresSafeArea()
                        .tag(idx)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .never))

            VStack {
                HStack {
                    Text("\(currentIndex + 1) / \(photos.count)")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.white)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(Capsule().fill(Color.black.opacity(0.55)))

                    Spacer()

                    Button { dismiss() } label: {
                        Image(systemName: "xmark")
                            .font(.system(size: 16, weight: .bold))
                            .foregroundColor(.white)
                            .frame(width: 40, height: 40)
                            .background(Circle().fill(Color.black.opacity(0.55)))
                    }
                }
                .padding(.horizontal, 20)
                .padding(.top, 12)

                Spacer()

                if photos.count > 1 {
                    HStack(spacing: 6) {
                        ForEach(0..<photos.count, id: \.self) { idx in
                            Circle()
                                .fill(idx == currentIndex
                                      ? color.color
                                      : Color.white.opacity(0.35))
                                .frame(width: 7, height: 7)
                        }
                    }
                    .padding(.bottom, 28)
                }
            }
        }
    }
}
