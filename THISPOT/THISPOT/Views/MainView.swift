//
//  MainView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct MainView: View {
    let nickname: String
    let characterAsset: String

    @StateObject private var locationManager = LocationManager()
    @StateObject private var weatherManager = WeatherManager()
    @State private var goToWalk = false
    @State private var todaysColor: WalkColor = .green

    // TODO: aggregate from saved walk history
    private let totalDistanceKm: Double = 0.0

    // Persisted across launches — written when a walk session ends
    @AppStorage("currentStreak") private var currentStreak: Int = 0
    @AppStorage("lastWalkDate") private var lastWalkDate: Double = 0
    @AppStorage("lastWalkDistanceKm") private var lastWalkDistanceKm: Double = 0
    @AppStorage("lastWalkDurationSec") private var lastWalkDurationSec: Int = 0

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)

    // Rotates daily so the prompt feels fresh
    private let colorWalkPrompts = [
        "What color will you chase today?",
        "Today's color is waiting outside.",
        "Step out and meet a new shade.",
        "Which hue is calling your name?",
        "Let's collect a color today.",
        "A new palette is out there.",
        "Go find a color worth keeping."
    ]

    private var dailyPrompt: String {
        let day = Calendar.current.ordinality(of: .day, in: .year, for: Date()) ?? 1
        return colorWalkPrompts[day % colorWalkPrompts.count]
    }

    private var hasLastWalk: Bool { lastWalkDate > 0 }

    private var lastWalkText: String {
        guard hasLastWalk else { return "Your first walk awaits ✨" }
        let date = Date(timeIntervalSince1970: lastWalkDate)
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        let when = formatter.localizedString(for: date, relativeTo: Date())
        let mins = max(1, lastWalkDurationSec / 60)
        return "\(when) · \(String(format: "%.1f km", lastWalkDistanceKm)) · \(mins) min"
    }

    var body: some View {
        ZStack {
            // MARK: - Soft background
            Image("background")
                .resizable()
                .scaledToFill()
                .ignoresSafeArea()
            backgroundCream.opacity(0.45).ignoresSafeArea()

            VStack(spacing: 0) {
                // MARK: - Greeting
                Text("Hello, \(nickname) ")
                    .font(.system(size: 26, weight: .bold))
                    .foregroundColor(textDark)
                    .padding(.top, 88)

                Text(dailyPrompt)
                    .font(.system(size: 15, weight: .medium))
                    .foregroundColor(brandBrown.opacity(0.9))
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 28)
                    .padding(.top, 6)

                // MARK: - Streak
                Text(currentStreak > 0
                     ? "🌱 \(currentStreak) day streak"
                     : "🌱 Start your streak today")
                    .font(.system(size: 13, weight: .semibold))
                    .foregroundColor(brandGreen)
                    .padding(.top, 8)

                // MARK: - Location + Weather chips
                HStack(spacing: 8) {
                    chip {
                        Image("location")
                            .resizable()
                            .scaledToFit()
                            .frame(width: 16, height: 16)
                        Text(locationManager.locationName)
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(brandBrown)
                    }

                    chip {
                        Text(weatherManager.symbol)
                            .font(.system(size: 13))
                        Text(weatherManager.temperatureText)
                            .font(.system(size: 13, weight: .medium))
                            .foregroundColor(brandBrown)
                    }
                }
                .padding(.top, 12)

                Spacer()

                // MARK: - Total distance
                VStack(spacing: 4) {
                    Text(String(format: "%.1f km", totalDistanceKm))
                        .font(.system(size: 32, weight: .bold))
                        .foregroundColor(brandGreen)
                    Text("Total walked")
                        .font(.system(size: 12, weight: .heavy))
                        .foregroundColor(brandBrown.opacity(0.85))
                        .tracking(1.6)
                        .textCase(.uppercase)
                }
                .padding(.bottom, 12)

                // MARK: - Character
                Image(characterAsset)
                    .resizable()
                    .scaledToFit()
                    .frame(maxWidth: 280, maxHeight: 320)

                // MARK: - Last walk summary
                Text(lastWalkText)
                    .font(.system(size: 13, weight: .bold))
                    .foregroundColor(brandBrown.opacity(0.85))
                    .padding(.top, 6)

                Spacer()

                // MARK: - Bottom controls
                HStack(alignment: .center) {
                    // Records (walk history)
                    Button {
                        // TODO: navigate to records / walk history
                    } label: {
                        VStack(spacing: 3) {
                            Image(systemName: "book.closed.fill")
                                .font(.system(size: 18, weight: .medium))
                            Text("Records")
                                .font(.system(size: 10, weight: .semibold))
                        }
                        .foregroundColor(brandBrown)
                        .frame(width: 64, height: 64)
                        .background(Circle().fill(Color.white.opacity(0.75)))
                        .overlay(Circle().stroke(brandBrown.opacity(0.15), lineWidth: 1))
                    }

                    Spacer()

                    // Let's Walk (primary)
                    Button {
                        todaysColor = .random()
                        goToWalk = true
                    } label: {
                        Text("Let's\nWalk")
                            .font(.system(size: 19, weight: .bold))
                            .foregroundColor(.white)
                            .multilineTextAlignment(.center)
                            .frame(width: 124, height: 124)
                            .background(Circle().fill(brandGreen))
                            .shadow(color: brandGreen.opacity(0.45), radius: 14, x: 0, y: 6)
                    }

                    Spacer()

                    // Symmetry placeholder so Let's Walk stays centered
                    Color.clear.frame(width: 64, height: 64)
                }
                .padding(.horizontal, 28)
                .padding(.bottom, 44)
            }
        }
        .navigationBarBackButtonHidden(true)
        .onAppear {
            locationManager.start()
        }
        .task(id: locationManager.location?.timestamp) {
            if let loc = locationManager.location {
                await weatherManager.fetch(for: loc)
            }
        }
        .navigationDestination(isPresented: $goToWalk) {
            WalkSessionView(
                nickname: nickname,
                characterAsset: characterAsset,
                todaysColor: todaysColor
            )
        }
    }

    // Reusable capsule chip
    @ViewBuilder
    private func chip<Content: View>(@ViewBuilder _ content: () -> Content) -> some View {
        HStack(spacing: 6) {
            content()
        }
        .padding(.horizontal, 14)
        .padding(.vertical, 7)
        .background(Capsule().fill(Color.white.opacity(0.75)))
        .overlay(Capsule().stroke(brandBrown.opacity(0.12), lineWidth: 1))
    }
}

#Preview {
    MainView(nickname: "Yeokyung", characterAsset: "charactor1")
}
