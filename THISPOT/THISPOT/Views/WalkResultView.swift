//
//  WalkResultView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct WalkResultView: View {
    let nickname: String
    let report: WalkReport
    let photos: [UIImage]
    var serverImageURL: URL? = nil
    let onHome: () -> Void
    let onViewDetail: () -> Void

    @State private var entryScale: CGFloat = 0.92
    @State private var entryOpacity: Double = 0
    @State private var selectedPhoto: PhotoSelection? = nil

    // POT overlay → shake → fade → photos cascade
    @State private var photosOut = false
    @State private var potOverlayVisible = true
    @State private var potOverlayScale: CGFloat = 0.55
    @State private var potOverlayOpacity: Double = 0
    @State private var potShakeRotation: CGFloat = 0
    @State private var potDimOpacity: Double = 0

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)

    var body: some View {
        ZStack {
            // MARK: - Background
            Image("background")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
            backgroundCream.opacity(0.55).ignoresSafeArea()
            report.color.color.opacity(0.10).ignoresSafeArea()

            ScrollView {
                VStack(spacing: 24) {
                    HStack {
                        Spacer()
                        homeButton
                    }
                    .padding(.horizontal, 20)
                    .padding(.top, 28)

                    // MARK: - Title + praise
                    VStack(spacing: 8) {
                        Text("Nice walk, \(nickname)!")
                            .font(.system(size: 26, weight: .bold))
                            .foregroundColor(textDark)

                        Text(praiseMessage)
                            .font(.system(size: 15, weight: .medium))
                            .foregroundColor(brandBrown.opacity(0.95))
                            .multilineTextAlignment(.center)
                            .padding(.horizontal, 30)
                    }

                    // MARK: - Photos
                    if photos.isEmpty {
                        emptyPhotosCard
                    } else {
                        photosGrid
                    }

                    // MARK: - Report card
                    reportCard

                    // MARK: - Primary CTA
                    Button(action: onViewDetail) {
                        HStack(spacing: 8) {
                            Text("View Results")
                                .font(.system(size: 17, weight: .bold))
                            Image(systemName: "arrow.right")
                                .font(.system(size: 14, weight: .bold))
                        }
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 16)
                        .background(
                            Capsule().fill(report.color.color)
                        )
                        .shadow(
                            color: report.color.color.opacity(0.45),
                            radius: 12, x: 0, y: 6
                        )
                    }
                    .buttonStyle(PressableScaleStyle())
                    .padding(.horizontal, 24)

                    Spacer(minLength: 32)
                }
                .scaleEffect(entryScale)
                .opacity(entryOpacity)
            }

            // MARK: - POT overlay (entrance → shake → burst → photos)
            if potOverlayVisible {
                ZStack {
                    Color.black
                        .opacity(potDimOpacity)
                        .ignoresSafeArea()

                    potOverlay
                }
                .zIndex(100)
                .allowsHitTesting(false)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar(.hidden, for: .navigationBar)
        .task {
            // Background content fades in normally
            withAnimation(.spring(response: 0.55, dampingFraction: 0.78)) {
                entryScale = 1.0
                entryOpacity = 1.0
            }

            // 1. Big POT springs in (with subtle dim behind)
            try? await Task.sleep(for: .milliseconds(150))
            withAnimation(.spring(response: 0.55, dampingFraction: 0.62)) {
                potOverlayScale = 1.0
                potOverlayOpacity = 1.0
                potDimOpacity = 0.18
            }

            // 2. Hold for a beat
            try? await Task.sleep(for: .milliseconds(550))

            // 3. Shake (quick oscillation)
            let shake: [CGFloat] = [-14, 14, -12, 12, -8, 8, -4, 4, 0]
            for angle in shake {
                withAnimation(.easeInOut(duration: 0.07)) {
                    potShakeRotation = angle
                }
                try? await Task.sleep(for: .milliseconds(75))
            }

            // 4. POT bursts open: scale up + fade out (lid flying off feel)
            withAnimation(.easeOut(duration: 0.5)) {
                potOverlayScale = 1.55
                potOverlayOpacity = 0
                potDimOpacity = 0
            }

            // 5. As POT fades, photos cascade in from where it was
            try? await Task.sleep(for: .milliseconds(180))
            photosOut = true

            // 6. Remove overlay from view tree
            try? await Task.sleep(for: .milliseconds(320))
            potOverlayVisible = false
        }
        .fullScreenCover(item: $selectedPhoto) { selection in
            PhotoViewer(image: photos[selection.index])
        }
    }

    // MARK: - Pieces

    private var praiseMessage: String {
        let count = photos.count
        let colorName = report.color.displayName.lowercased()
        switch count {
        case 0:
            return "Even a quiet walk is a good walk."
        case 1:
            return "You found 1 \(colorName) moment today."
        case 2...4:
            return "You collected \(count) \(colorName) moments today."
        default:
            return "What a haul — \(count) \(colorName) finds today."
        }
    }

    /// The hero POT shown center-screen during the result intro.
    /// Springs in, shakes, then bursts open as photos cascade out.
    private var potOverlay: some View {
        ZStack {
            // Color halo behind the pot
            Circle()
                .fill(report.color.color.opacity(0.32))
                .frame(width: 320, height: 320)
                .blur(radius: 38)
                .opacity(potOverlayOpacity)

            potHeroImage
                .scaleEffect(potOverlayScale)
                .rotationEffect(.degrees(potShakeRotation))
                .opacity(potOverlayOpacity)
        }
    }

    @ViewBuilder
    private var potHeroImage: some View {
        if UIImage(named: "pots") != nil {
            Image("pots")
                .resizable()
                .scaledToFit()
                .frame(width: 240, height: 240)
                .shadow(color: brandBrown.opacity(0.35), radius: 18, x: 0, y: 10)
                .shadow(color: report.color.color.opacity(0.45), radius: 28)
        } else {
            Image(systemName: "tray.full.fill")
                .font(.system(size: 110, weight: .medium))
                .foregroundColor(brandBrown)
                .frame(width: 240, height: 240)
                .background(Circle().fill(Color.white.opacity(0.85)))
                .shadow(color: brandBrown.opacity(0.30), radius: 14, x: 0, y: 6)
        }
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

    private var photosGrid: some View {
        let columns = [
            GridItem(.flexible(), spacing: 10),
            GridItem(.flexible(), spacing: 10)
        ]
        return LazyVGrid(columns: columns, spacing: 10) {
            ForEach(Array(photos.enumerated()), id: \.offset) { idx, img in
                Button {
                    selectedPhoto = PhotoSelection(index: idx)
                } label: {
                    Image(uiImage: img)
                        .resizable()
                        .scaledToFill()
                        .frame(height: 150)
                        .clipped()
                        .clipShape(RoundedRectangle(cornerRadius: 16, style: .continuous))
                        .overlay(
                            RoundedRectangle(cornerRadius: 16, style: .continuous)
                                .stroke(Color.white, lineWidth: 2.5)
                        )
                        .shadow(color: brandBrown.opacity(0.20), radius: 6, x: 0, y: 3)
                }
                .buttonStyle(PressableScaleStyle())
                // Photos appear to fly out of the pot (which sits above the grid)
                .scaleEffect(photosOut ? 1.0 : 0.1)
                .opacity(photosOut ? 1.0 : 0)
                .offset(y: photosOut ? 0 : -260)
                .rotationEffect(.degrees(photosOut ? 0 : (idx.isMultiple(of: 2) ? -14 : 14)))
                .animation(
                    .spring(response: 0.65, dampingFraction: 0.7)
                        .delay(Double(idx) * 0.09),
                    value: photosOut
                )
            }
        }
        .padding(.horizontal, 20)
    }

    private var emptyPhotosCard: some View {
        VStack(spacing: 10) {
            Image(systemName: "photo")
                .font(.system(size: 30))
                .foregroundColor(brandBrown.opacity(0.45))
            Text("No photos this time")
                .font(.system(size: 13, weight: .medium))
                .foregroundColor(brandBrown.opacity(0.7))
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 36)
        .background(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(Color.white.opacity(0.7))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(brandBrown.opacity(0.10), lineWidth: 1)
        )
        .padding(.horizontal, 20)
    }

    private var reportCard: some View {
        HStack(spacing: 0) {
            stat(
                value: String(format: "%.2f", report.distanceKm),
                unit: "km",
                label: "Distance"
            )
            divider
            stat(
                value: "\(photos.count)",
                unit: "",
                label: "Photos"
            )
            divider
            stat(
                value: "~\(report.calories)",
                unit: "kcal",
                label: "Calories"
            )
        }
        .padding(.vertical, 18)
        .background(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(Color.white.opacity(0.92))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(report.color.color.opacity(0.30), lineWidth: 1)
        )
        .shadow(color: brandBrown.opacity(0.15), radius: 10, x: 0, y: 4)
        .padding(.horizontal, 20)
    }

    private func stat(value: String, unit: String, label: String) -> some View {
        VStack(spacing: 4) {
            HStack(alignment: .firstTextBaseline, spacing: 2) {
                Text(value)
                    .font(.system(size: 22, weight: .bold))
                    .foregroundColor(report.color.color)
                if !unit.isEmpty {
                    Text(unit)
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundColor(brandBrown.opacity(0.85))
                }
            }
            Text(label)
                .font(.system(size: 10, weight: .semibold))
                .tracking(1.4)
                .textCase(.uppercase)
                .foregroundColor(brandBrown.opacity(0.75))
        }
        .frame(maxWidth: .infinity)
    }

    private var divider: some View {
        Rectangle()
            .fill(brandBrown.opacity(0.12))
            .frame(width: 1, height: 32)
    }
}

#Preview {
    WalkResultView(
        nickname: "Yeokyung",
        report: WalkReport(
            id: UUID(),
            color: .green,
            distanceMeters: 1234,
            durationSec: 720,
            photoCount: 3,
            endedAt: Date()
        ),
        photos: [],
        onHome: {},
        onViewDetail: {}
    )
}
