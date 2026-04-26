//
//  WalkSessionView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI
import MapKit
import CoreLocation
import Photos

struct WalkSessionView: View {
    let nickname: String
    let characterAsset: String
    let todaysColor: WalkColor

    @Environment(\.dismiss) private var dismiss
    @StateObject private var tracker = WalkTracker()

    @State private var cameraPosition: MapCameraPosition = .userLocation(
        followsHeading: false,
        fallback: .automatic
    )

    // Camera + photo state
    @State private var showCamera = false
    @State private var capturedImage: UIImage? = nil
    @State private var capturedImages: [UIImage] = []
    @State private var selectedPhoto: PhotoSelection? = nil

    // Pulse + reveal animation
    @State private var pickPulse = false
    @State private var showReveal = true
    @State private var revealScale: CGFloat = 0.65

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)

    var body: some View {
        ZStack {
            // MARK: - Map
            Map(position: $cameraPosition) {
                UserAnnotation()
                if tracker.path.count >= 2 {
                    MapPolyline(coordinates: tracker.path)
                        .stroke(todaysColor.color, lineWidth: 5)
                }
            }
            .mapStyle(.standard(elevation: .flat, pointsOfInterest: .excludingAll))
            .ignoresSafeArea()

            // Cream tint to harmonize the map with the rest of the app
            backgroundCream.opacity(0.18).ignoresSafeArea().allowsHitTesting(false)

            VStack(spacing: 0) {
                topBar
                    .padding(.horizontal, 20)
                    .padding(.top, 8)

                Spacer()

                if !capturedImages.isEmpty {
                    photoStrip
                        .padding(.horizontal, 20)
                        .padding(.bottom, 12)
                }

                bottomBar
                    .padding(.horizontal, 24)
                    .padding(.bottom, 36)
            }

            // MARK: - Today's Color reveal (splash-style)
            if showReveal {
                colorReveal
                    .transition(.opacity)
                    .zIndex(10)
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar(.hidden, for: .navigationBar)
        .task {
            tracker.start()
            withAnimation(.easeInOut(duration: 1.4).repeatForever(autoreverses: true)) {
                pickPulse = true
            }
            // Spring the reveal text in after the view settles
            try? await Task.sleep(for: .milliseconds(80))
            withAnimation(.spring(response: 0.55, dampingFraction: 0.65)) {
                revealScale = 1.0
            }
            // Hold then fade out to map
            try? await Task.sleep(for: .milliseconds(1700))
            withAnimation(.easeInOut(duration: 0.45)) {
                showReveal = false
            }
        }
        .onDisappear { tracker.stop() }
        .onChange(of: capturedImage) { _, newValue in
            guard let img = newValue else { return }
            capturedImages.append(img)
            saveToPhotoLibrary(img)
            capturedImage = nil
        }
        .fullScreenCover(isPresented: $showCamera) {
            CameraPicker(image: $capturedImage)
                .ignoresSafeArea()
        }
        .fullScreenCover(item: $selectedPhoto) { selection in
            PhotoViewer(image: capturedImages[selection.index])
        }
    }

    // MARK: - Color reveal
    private var colorReveal: some View {
        ZStack {
            todaysColor.color.ignoresSafeArea()

            VStack(spacing: 14) {
                Text("Today's Color is")
                    .font(.system(size: 22, weight: .semibold))
                    .foregroundColor(.white.opacity(0.92))
                    .tracking(0.5)

                Text("\(todaysColor.displayName)!!")
                    .font(.system(size: 56, weight: .heavy))
                    .foregroundColor(.white)
                    .shadow(color: todaysColor.deepColor.opacity(0.35), radius: 8, x: 0, y: 4)
            }
            .scaleEffect(revealScale)
        }
    }

    // MARK: - Top bar
    private var topBar: some View {
        HStack(alignment: .top) {
            backButton
            Spacer(minLength: 12)
            VStack(spacing: 8) {
                distanceCard
                todaysColorChip
            }
            Spacer(minLength: 12)
            finishButton
        }
    }

    private var backButton: some View {
        Button {
            tracker.stop()
            dismiss()
        } label: {
            Image(systemName: "chevron.left")
                .font(.system(size: 16, weight: .semibold))
                .foregroundColor(brandBrown)
                .frame(width: 40, height: 40)
                .background(Circle().fill(Color.white.opacity(0.85)))
                .overlay(Circle().stroke(brandBrown.opacity(0.15), lineWidth: 1))
                .shadow(color: brandBrown.opacity(0.12), radius: 6, x: 0, y: 2)
        }
    }

    private var finishButton: some View {
        Button {
            finishWalk()
        } label: {
            Text("Finish")
                .font(.system(size: 13, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 11)
                .background(Capsule().fill(brandBrown))
                .shadow(color: brandBrown.opacity(0.30), radius: 6, x: 0, y: 3)
        }
        .buttonStyle(PressableScaleStyle())
    }

    private func finishWalk() {
        tracker.stop()
        dismiss()
    }

    private var distanceCard: some View {
        VStack(spacing: 2) {
            Text(formattedDistance)
                .font(.system(size: 22, weight: .bold))
                .foregroundColor(brandGreen)
                .contentTransition(.numericText())
                .animation(.easeInOut(duration: 0.25), value: tracker.distanceMeters)

            Text("Distance")
                .font(.system(size: 10, weight: .semibold))
                .tracking(1.6)
                .textCase(.uppercase)
                .foregroundColor(brandBrown.opacity(0.75))
        }
        .padding(.horizontal, 22)
        .padding(.vertical, 10)
        .background(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .fill(Color.white.opacity(0.9))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 18, style: .continuous)
                .stroke(brandBrown.opacity(0.10), lineWidth: 1)
        )
        .shadow(color: brandBrown.opacity(0.15), radius: 10, x: 0, y: 4)
    }

    private var todaysColorChip: some View {
        HStack(spacing: 6) {
            Circle()
                .fill(todaysColor.color)
                .frame(width: 9, height: 9)
                .shadow(color: todaysColor.color.opacity(0.55), radius: 4)

            Text("Today's Color: \(todaysColor.displayName)")
                .font(.system(size: 11, weight: .semibold))
                .foregroundColor(brandBrown)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 6)
        .background(Capsule().fill(Color.white.opacity(0.92)))
        .overlay(Capsule().stroke(todaysColor.color.opacity(0.35), lineWidth: 1))
        .shadow(color: brandBrown.opacity(0.10), radius: 6, x: 0, y: 2)
    }

    private var formattedDistance: String {
        let km = tracker.distanceKm
        if km < 1 {
            return String(format: "%.0f m", tracker.distanceMeters)
        } else {
            return String(format: "%.2f km", km)
        }
    }

    // MARK: - Photo strip (above bottom controls)
    private var photoStrip: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 10) {
                ForEach(Array(capturedImages.enumerated()), id: \.offset) { idx, img in
                    Button {
                        selectedPhoto = PhotoSelection(index: idx)
                    } label: {
                        Image(uiImage: img)
                            .resizable()
                            .scaledToFill()
                            .frame(width: 64, height: 64)
                            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
                            .overlay(
                                RoundedRectangle(cornerRadius: 14, style: .continuous)
                                    .stroke(Color.white, lineWidth: 2)
                            )
                            .shadow(color: brandBrown.opacity(0.25), radius: 5, x: 0, y: 2)
                    }
                    .buttonStyle(PressableScaleStyle())
                }
            }
            .padding(.horizontal, 14)
            .padding(.vertical, 12)
        }
        .background(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .fill(Color.white.opacity(0.85))
        )
        .overlay(
            RoundedRectangle(cornerRadius: 22, style: .continuous)
                .stroke(brandBrown.opacity(0.10), lineWidth: 1)
        )
        .shadow(color: brandBrown.opacity(0.10), radius: 8, x: 0, y: 3)
    }

    // MARK: - Bottom bar
    private var bottomBar: some View {
        HStack(alignment: .bottom) {
            walkingChip
            Spacer()
            cameraButton
        }
    }

    private var walkingChip: some View {
        HStack(spacing: 8) {
            Circle()
                .fill(todaysColor.color)
                .frame(width: 8, height: 8)
                .scaleEffect(pickPulse ? 1.25 : 0.85)
                .opacity(pickPulse ? 1.0 : 0.6)

            Text("Walking with \(todaysColor.displayName.lowercased())")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(brandBrown)
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 8)
        .background(
            Capsule().fill(Color.white.opacity(0.9))
        )
        .overlay(
            Capsule().stroke(brandBrown.opacity(0.12), lineWidth: 1)
        )
        .shadow(color: brandBrown.opacity(0.10), radius: 6, x: 0, y: 2)
    }

    // MARK: - Camera button (bare PNG, no circle)
    private var cameraButton: some View {
        VStack(spacing: 8) {
            // "Let's Pick!" speech-bubble hint
            Text("Let's Pick!")
                .font(.system(size: 12, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 14)
                .padding(.vertical, 6)
                .background(Capsule().fill(brandBrown))
                .overlay(alignment: .bottom) {
                    Triangle()
                        .fill(brandBrown)
                        .frame(width: 10, height: 6)
                        .offset(y: 5)
                }
                .shadow(color: brandBrown.opacity(0.30), radius: 6, x: 0, y: 3)
                .scaleEffect(pickPulse ? 1.04 : 0.96)

            Button {
                showCamera = true
            } label: {
                cameraGlyph
            }
            .buttonStyle(PressableScaleStyle())
        }
    }

    /// Renders the `camera` PNG directly when present. Falls back to an SF
    /// Symbol so the layout still works before the asset is added.
    @ViewBuilder
    private var cameraGlyph: some View {
        if UIImage(named: "camera") != nil {
            Image("camera")
                .resizable()
                .scaledToFit()
                .frame(width: 84, height: 84)
                .shadow(color: brandBrown.opacity(0.30), radius: 10, x: 0, y: 4)
        } else {
            Image(systemName: "camera.fill")
                .font(.system(size: 36, weight: .semibold))
                .foregroundColor(brandBrown)
                .frame(width: 78, height: 78)
                .background(Circle().fill(Color.white.opacity(0.95)))
                .shadow(color: brandBrown.opacity(0.20), radius: 8, x: 0, y: 3)
        }
    }

    // MARK: - Photo library
    private func saveToPhotoLibrary(_ img: UIImage) {
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else { return }
            PHPhotoLibrary.shared().performChanges {
                PHAssetCreationRequest.creationRequestForAsset(from: img)
            } completionHandler: { _, _ in }
        }
    }
}

// MARK: - Helpers

private struct PhotoSelection: Identifiable {
    let index: Int
    var id: Int { index }
}

private struct PhotoViewer: View {
    let image: UIImage
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        ZStack {
            Color.black.ignoresSafeArea()

            Image(uiImage: image)
                .resizable()
                .scaledToFit()
                .ignoresSafeArea()

            VStack {
                HStack {
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
            }
        }
    }
}

private struct Triangle: Shape {
    func path(in rect: CGRect) -> Path {
        var p = Path()
        p.move(to: CGPoint(x: rect.midX, y: rect.maxY))
        p.addLine(to: CGPoint(x: rect.minX, y: rect.minY))
        p.addLine(to: CGPoint(x: rect.maxX, y: rect.minY))
        p.closeSubpath()
        return p
    }
}

private struct PressableScaleStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.94 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.7), value: configuration.isPressed)
    }
}

#Preview {
    NavigationStack {
        WalkSessionView(
            nickname: "Yeokyung",
            characterAsset: "charactor1",
            todaysColor: .green
        )
    }
}
