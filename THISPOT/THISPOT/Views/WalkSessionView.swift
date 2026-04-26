//
//  WalkSessionView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI
import MapKit
import CoreLocation

struct WalkSessionView: View {
    let nickname: String
    let characterAsset: String
    let todaysColor: WalkColor

    @Environment(\.dismiss) private var dismiss
    @StateObject private var tracker = WalkTracker()

    private enum Phase { case walking, result, detail }
    @State private var phase: Phase = .walking
    @State private var report: WalkReport? = nil

    @State private var walkID = UUID().uuidString
    @State private var walkStartTime = Date()

    @State private var cameraPosition: MapCameraPosition = .userLocation(
        followsHeading: false,
        fallback: .automatic
    )

    // Camera + photo state
    @State private var showCamera = false
    @State private var capturedImage: UIImage? = nil
    @State private var capturedImages: [UIImage] = []
    @State private var photoIDs: [String] = []
    @State private var showPotGallery = false

    // Upload state
    @State private var uploadInFlight = false
    @State private var feedbackText: String? = nil
    @State private var feedbackIsSuccess = false

    // Aggregated for /api/finish-walk
    @State private var bestMatchScore: Double = 0
    @State private var isNewSpot: Bool = false

    // Finish state
    @State private var isFinishing = false
    @State private var serverImageURL: URL? = nil
    @State private var serverBadge: ThiSpotAPI.FinishWalkResponse.Badge? = nil

    // Pulse + reveal animation
    @State private var pickPulse = false
    @State private var showReveal = true
    @State private var revealScale: CGFloat = 0.65
    @State private var potBounceScale: CGFloat = 1.0

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)

    var body: some View {
        Group {
            switch phase {
            case .walking:
                walkingPhase
            case .result:
                if let report {
                    WalkResultView(
                        nickname: nickname,
                        report: report,
                        photos: capturedImages,
                        serverImageURL: serverImageURL,
                        onHome: { dismiss() },
                        onViewDetail: {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                phase = .detail
                            }
                        }
                    )
                    .transition(.opacity)
                }
            case .detail:
                if let report {
                    WalkResultDetailView(
                        color: report.color,
                        imageURL: serverImageURL,
                        badge: serverBadge,
                        onBack: {
                            withAnimation(.easeInOut(duration: 0.3)) {
                                phase = .result
                            }
                        },
                        onHome: { dismiss() }
                    )
                    .transition(.opacity)
                }
            }
        }
        .navigationBarBackButtonHidden(true)
        .toolbar(.hidden, for: .navigationBar)
    }

    // MARK: - Walking phase
    private var walkingPhase: some View {
        ZStack {
            // MARK: Map
            Map(position: $cameraPosition) {
                UserAnnotation()
                if tracker.path.count >= 2 {
                    MapPolyline(coordinates: tracker.path)
                        .stroke(todaysColor.color, lineWidth: 5)
                }
            }
            .mapStyle(.standard(elevation: .flat, pointsOfInterest: .excludingAll))
            .ignoresSafeArea()

            backgroundCream.opacity(0.18)
                .ignoresSafeArea()
                .allowsHitTesting(false)

            VStack(spacing: 0) {
                topBar
                    .padding(.horizontal, 20)
                    .padding(.top, 8)

                Spacer()

                bottomBar
                    .padding(.horizontal, 24)
                    .padding(.bottom, 36)
            }

            // MARK: Today's Color reveal (splash-style)
            if showReveal {
                colorReveal
                    .transition(.opacity)
                    .zIndex(10)
            }

            // MARK: Upload feedback toast
            if let text = feedbackText {
                feedbackToast(text: text, isSuccess: feedbackIsSuccess)
                    .transition(.move(edge: .top).combined(with: .opacity))
                    .zIndex(20)
            }
        }
        .animation(.spring(response: 0.4, dampingFraction: 0.8), value: feedbackText)
        .task {
            tracker.start()
            withAnimation(.easeInOut(duration: 1.4).repeatForever(autoreverses: true)) {
                pickPulse = true
            }
            try? await Task.sleep(for: .milliseconds(80))
            withAnimation(.spring(response: 0.55, dampingFraction: 0.65)) {
                revealScale = 1.0
            }
            try? await Task.sleep(for: .milliseconds(1700))
            withAnimation(.easeInOut(duration: 0.45)) {
                showReveal = false
            }
        }
        .onDisappear { tracker.stop() }
        .onChange(of: capturedImage) { _, newValue in
            guard let img = newValue else { return }
            capturedImage = nil
            Task { await uploadAndStore(img) }
        }
        .fullScreenCover(isPresented: $showCamera) {
            CameraPicker(image: $capturedImage)
                .ignoresSafeArea()
        }
        .fullScreenCover(isPresented: $showPotGallery) {
            PotGalleryView(photos: capturedImages, color: todaysColor)
        }
    }

    private func triggerPotBounce() {
        withAnimation(.spring(response: 0.25, dampingFraction: 0.45)) {
            potBounceScale = 1.20
        }
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.20) {
            withAnimation(.spring(response: 0.45, dampingFraction: 0.7)) {
                potBounceScale = 1.0
            }
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
            Task { await finishWalk() }
        } label: {
            ZStack {
                Text("Finish")
                    .font(.system(size: 13, weight: .bold))
                    .foregroundColor(.white)
                    .opacity(isFinishing ? 0 : 1)
                if isFinishing {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(.white)
                        .scaleEffect(0.8)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 11)
            .background(Capsule().fill(brandBrown))
            .shadow(color: brandBrown.opacity(0.30), radius: 6, x: 0, y: 3)
        }
        .buttonStyle(PressableScaleStyle())
        .disabled(isFinishing)
    }

    private func finishWalk() async {
        guard !isFinishing else { return }
        isFinishing = true
        defer { isFinishing = false }

        tracker.stop()
        let durationSec = max(1, Int(Date().timeIntervalSince(walkStartTime)))
        let distanceM = Int(tracker.distanceMeters.rounded())

        // Local report — used immediately for the result screen, even if the
        // server call fails so the user always sees a report card.
        let localReport = WalkReport(
            id: UUID(uuidString: walkID) ?? UUID(),
            color: todaysColor,
            distanceMeters: tracker.distanceMeters,
            durationSec: durationSec,
            photoCount: capturedImages.count,
            endedAt: Date()
        )

        do {
            let resp = try await ThiSpotAPI.finishWalk(
                userID: "demo_user",
                sessionID: walkID,
                targetColor: todaysColor.rawValue,
                distanceM: distanceM,
                steps: 0, // TODO: integrate CMPedometer
                durationSec: durationSec,
                photoIDs: photoIDs,
                bestMatchScore: bestMatchScore,
                isNewSpot: isNewSpot
            )

            serverBadge = resp.badge

            // Resolve final report — poll if queued.
            var finalReport: ThiSpotAPI.FinishWalkResponse.Report? = resp.report
            if resp.report?.status == "queued",
               let jobID = resp.report?.generation_job_id {
                finalReport = await pollGenerationJob(jobID: jobID, maxSeconds: 90)
                    ?? resp.report
            }

            if let urlStr = finalReport?.image_url,
               let url = ThiSpotAPI.rewriteServerURL(urlStr) {
                // Download once, save to disk so Records picks it up too.
                // Detail view then renders the local file (no second fetch).
                if let localURL = await WalkPhotoStore.saveRemoteReport(
                    from: url, walkID: walkID
                ) {
                    serverImageURL = localURL
                } else {
                    serverImageURL = url // remote fallback if save failed
                }
            }
        } catch {
            #if DEBUG
            print("[finishWalk] failed:", error)
            #endif
            // Continue to result screen even on failure
        }

        report = localReport
        withAnimation(.easeInOut(duration: 0.4)) {
            phase = .result
        }
    }

    /// Polls /api/generation-jobs/{id} every 2s until status is no longer
    /// queued/running, or until `maxSeconds` elapses. Returns the final report
    /// if completed/fallback, nil otherwise.
    private func pollGenerationJob(
        jobID: String,
        maxSeconds: Int
    ) async -> ThiSpotAPI.FinishWalkResponse.Report? {
        let attempts = max(1, maxSeconds / 2)
        for _ in 0..<attempts {
            try? await Task.sleep(nanoseconds: 2_000_000_000) // 2s
            do {
                let job = try await ThiSpotAPI.getGenerationJob(jobID: jobID)
                switch job.status {
                case "completed", "fallback":
                    return job.report
                case "failed":
                    return nil
                default:
                    continue // queued / running
                }
            } catch {
                #if DEBUG
                print("[pollGenerationJob] error:", error)
                #endif
                continue
            }
        }
        return nil // timed out
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
        .background(Capsule().fill(Color.white.opacity(0.9)))
        .overlay(Capsule().stroke(brandBrown.opacity(0.12), lineWidth: 1))
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
                    DownTriangle()
                        .fill(brandBrown)
                        .frame(width: 10, height: 6)
                        .offset(y: 5)
                }
                .shadow(color: brandBrown.opacity(0.30), radius: 6, x: 0, y: 3)
                .scaleEffect(pickPulse ? 1.04 : 0.96)

            Button {
                showCamera = true
            } label: {
                ZStack {
                    cameraGlyph
                        .opacity(uploadInFlight ? 0.5 : 1)
                    if uploadInFlight {
                        ProgressView()
                            .progressViewStyle(.circular)
                            .tint(brandBrown)
                            .scaleEffect(1.2)
                    }
                }
            }
            .buttonStyle(PressableScaleStyle())
            .disabled(uploadInFlight)
        }
    }

    // MARK: - Backend integration

    private func uploadAndStore(_ img: UIImage) async {
        uploadInFlight = true
        defer { uploadInFlight = false }

        let lat = tracker.path.last?.latitude
        let lng = tracker.path.last?.longitude

        do {
            let resp = try await ThiSpotAPI.analyzePhoto(
                image: img,
                userID: "demo_user", // TODO: from /api/login-demo
                sessionID: walkID,
                targetColor: todaysColor.rawValue,
                lat: lat,
                lng: lng
            )

            if resp.proof_result.accepted {
                // Save locally only on accepted proof
                capturedImages.append(img)
                WalkPhotoStore.save(img, walkID: walkID)
                photoIDs.append(resp.photo_id)
                triggerPotBounce()

                // Aggregate stats for /api/finish-walk
                if let score = resp.vision_result?.match_score {
                    bestMatchScore = max(bestMatchScore, score)
                }
                if resp.discovery_result?.is_new_spot == true {
                    isNewSpot = true
                }

                let count = "\(resp.proof_result.accepted_count)/\(resp.proof_result.required_count)"
                let base = resp.vision_result?.feedback ?? "Nice find!"
                showFeedback(success: true, text: "\(base) (\(count))")
            } else {
                let msg = resp.vision_result?.feedback
                    ?? "Hmm, not quite \(todaysColor.displayName.lowercased()). Try another shot."
                showFeedback(success: false, text: msg)
            }
        } catch {
            #if DEBUG
            print("[analyzePhoto] error:", error)
            #endif
            showFeedback(success: false,
                         text: error.localizedDescription)
        }
    }

    private func showFeedback(success: Bool, text: String) {
        feedbackIsSuccess = success
        feedbackText = text
        let snapshot = text
        Task {
            try? await Task.sleep(for: .seconds(3))
            if feedbackText == snapshot {
                feedbackText = nil
            }
        }
    }

    @ViewBuilder
    private func feedbackToast(text: String, isSuccess: Bool) -> some View {
        VStack {
            HStack(spacing: 10) {
                Image(systemName: isSuccess
                      ? "checkmark.circle.fill"
                      : "exclamationmark.triangle.fill")
                    .font(.system(size: 18, weight: .bold))
                Text(text)
                    .font(.system(size: 13, weight: .semibold))
                    .multilineTextAlignment(.leading)
                    .lineLimit(3)
            }
            .foregroundColor(.white)
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                Capsule().fill(
                    isSuccess
                    ? brandGreen
                    : Color(red: 0.85, green: 0.35, blue: 0.30)
                )
            )
            .shadow(color: .black.opacity(0.18), radius: 8, x: 0, y: 4)
            .padding(.horizontal, 24)
            .padding(.top, 90)
            Spacer()
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
