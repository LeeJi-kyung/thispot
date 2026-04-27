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
    var badge: ThiSpotAPI.FinishWalkResponse.Badge? = nil
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

                Spacer()

                if let badge {
                    badgeHero(badge)
                        .padding(.horizontal, 28)
                        .scaleEffect(entryScale)
                        .opacity(entryOpacity)
                }

                Spacer()
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

    @ViewBuilder
    private func badgeHero(_ badge: ThiSpotAPI.FinishWalkResponse.Badge) -> some View {
        VStack(spacing: 18) {
            if let urlStr = badge.image_url,
               let url = ThiSpotAPI.rewriteServerURL(urlStr) {
                AsyncImage(url: url) { phase in
                    switch phase {
                    case .success(let image):
                        image
                            .resizable()
                            .scaledToFit()
                    case .empty:
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(brandBrown)
                            .scaleEffect(1.4)
                    default:
                        Color.clear
                    }
                }
                .frame(maxWidth: 320, maxHeight: 360)
            }

            if let title = badge.title, !title.isEmpty {
                Text(title)
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(textDark)
                    .multilineTextAlignment(.center)
            }

            if let desc = badge.description, !desc.isEmpty {
                Text(desc)
                    .font(.system(size: 13, weight: .medium))
                    .foregroundColor(brandBrown.opacity(0.85))
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
            }

            if let rarity = badge.rarity, !rarity.isEmpty {
                Text(rarity.uppercased())
                    .font(.system(size: 10, weight: .heavy))
                    .tracking(1.8)
                    .foregroundColor(.white)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 5)
                    .background(Capsule().fill(rarityColor(rarity)))
            }
        }
    }

    private func rarityColor(_ rarity: String) -> Color {
        switch rarity.lowercased() {
        case "common":    return Color(red: 0.55, green: 0.55, blue: 0.55)
        case "rare":      return color.color
        case "epic":      return Color(red: 0.55, green: 0.35, blue: 0.75)
        case "legendary": return Color(red: 0.92, green: 0.62, blue: 0.20)
        default:          return color.color
        }
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
