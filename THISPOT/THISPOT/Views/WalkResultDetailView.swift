//
//  WalkResultDetailView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct WalkResultDetailView: View {
    let color: WalkColor
    var imageURL: URL? = nil
    let onBack: () -> Void
    let onHome: () -> Void

    @State private var entryScale: CGFloat = 0.92
    @State private var entryOpacity: Double = 0

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)

    var body: some View {
        ZStack {
            // Background
            Image("background")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
            backgroundCream.opacity(0.55).ignoresSafeArea()
            color.color.opacity(0.10).ignoresSafeArea()

            VStack(spacing: 0) {
                // Top bar
                HStack {
                    backButton
                    Spacer()
                    homeButton
                }
                .padding(.horizontal, 20)
                .padding(.top, 28)

                Spacer(minLength: 16)

                VStack(spacing: 6) {
                    Text("Today's Result")
                        .font(.system(size: 12, weight: .bold))
                        .tracking(1.8)
                        .textCase(.uppercase)
                        .foregroundColor(brandBrown.opacity(0.75))

                    Text("\(color.displayName) Story")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(textDark)
                }

                Spacer(minLength: 20)

                resultPng
                    .padding(.horizontal, 28)
                    .scaleEffect(entryScale)
                    .opacity(entryOpacity)

                Spacer()

                Text("More results will appear here soon.")
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(brandBrown.opacity(0.65))
                    .padding(.bottom, 28)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar(.hidden, for: .navigationBar)
        .task {
            withAnimation(.spring(response: 0.55, dampingFraction: 0.78)) {
                entryScale = 1.0
                entryOpacity = 1.0
            }
        }
    }

    /// Server-generated PNG (`/api/finish-walk` → report.image_url) is the
    /// primary content. Falls back to bundled `result` / `POT` if the URL is
    /// missing or fails to load.
    @ViewBuilder
    private var resultPng: some View {
        if let url = imageURL {
            AsyncImage(url: url) { phase in
                switch phase {
                case .empty:
                    placeholderCard {
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(brandBrown)
                            .scaleEffect(1.4)
                    }
                case .success(let image):
                    image
                        .resizable()
                        .scaledToFit()
                        .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 28, style: .continuous)
                                .stroke(color.color.opacity(0.25), lineWidth: 1.5)
                        )
                        .shadow(color: brandBrown.opacity(0.20), radius: 14, x: 0, y: 8)
                case .failure:
                    fallbackPng
                @unknown default:
                    fallbackPng
                }
            }
        } else {
            fallbackPng
        }
    }

    @ViewBuilder
    private var fallbackPng: some View {
        if UIImage(named: "result") != nil {
            Image("result")
                .resizable()
                .scaledToFit()
                .clipShape(RoundedRectangle(cornerRadius: 28, style: .continuous))
                .overlay(
                    RoundedRectangle(cornerRadius: 28, style: .continuous)
                        .stroke(color.color.opacity(0.25), lineWidth: 1.5)
                )
                .shadow(color: brandBrown.opacity(0.20), radius: 14, x: 0, y: 8)
        } else if UIImage(named: "POT") != nil {
            placeholderCard {
                Image("POT")
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 220)
            }
        } else {
            placeholderCard {
                Image(systemName: "photo.on.rectangle.angled")
                    .font(.system(size: 70))
                    .foregroundColor(brandBrown.opacity(0.4))
            }
        }
    }

    @ViewBuilder
    private func placeholderCard<C: View>(@ViewBuilder _ content: () -> C) -> some View {
        VStack(spacing: 14) {
            content()
            Text("Your story is on its way…")
                .font(.system(size: 13, weight: .semibold))
                .foregroundColor(brandBrown.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 38)
        .padding(.horizontal, 18)
        .background(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .fill(Color.white.opacity(0.88))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 28, style: .continuous)
                .stroke(color.color.opacity(0.30), lineWidth: 1.5)
        )
        .shadow(color: brandBrown.opacity(0.15), radius: 12, x: 0, y: 5)
    }

    private var backButton: some View {
        Button(action: onBack) {
            Image(systemName: "chevron.left")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(brandBrown)
                .frame(width: 40, height: 40)
                .background(Circle().fill(Color.white.opacity(0.9)))
                .overlay(Circle().stroke(brandBrown.opacity(0.15), lineWidth: 1))
                .shadow(color: brandBrown.opacity(0.12), radius: 6, x: 0, y: 2)
        }
        .buttonStyle(PressableScaleStyle())
    }

    private var homeButton: some View {
        Button(action: onHome) {
            Image(systemName: "house.fill")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(brandBrown)
                .frame(width: 40, height: 40)
                .background(Circle().fill(Color.white.opacity(0.9)))
                .overlay(Circle().stroke(brandBrown.opacity(0.15), lineWidth: 1))
                .shadow(color: brandBrown.opacity(0.12), radius: 6, x: 0, y: 2)
        }
        .buttonStyle(PressableScaleStyle())
    }
}

#Preview {
    WalkResultDetailView(color: .green, onBack: {}, onHome: {})
}
