//
//  CharacterSelectView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct CharacterSelectView: View {
    let nickname: String

    @Environment(\.dismiss) private var dismiss

    private let characters = ["charactor1", "charactor2", "charactor3", "charactor4"]
    @State private var selectedIndex: Int? = nil
    @State private var goToMain: Bool = false

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)
    private let placeholderGray = Color(red: 0.70, green: 0.70, blue: 0.70)

    var isDoneEnabled: Bool { selectedIndex != nil }

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
                        .background(
                            Circle()
                                .fill(Color.white.opacity(0.7))
                        )
                        .overlay(
                            Circle()
                                .stroke(brandBrown.opacity(0.15), lineWidth: 1)
                        )
                }
                .padding(.top, 8)
                .padding(.horizontal, 20)

                // MARK: - Title
                Text("Choose Your Character")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(textDark)
                    .padding(.top, 24)
                    .padding(.horizontal, 28)

                Text("Pick a buddy to walk with you.")
                    .font(.system(size: 14))
                    .foregroundColor(brandBrown.opacity(0.8))
                    .padding(.top, 8)
                    .padding(.horizontal, 28)

                Spacer().frame(height: 16)

                // MARK: - Selected Preview (no background)
                ZStack {
                    if let idx = selectedIndex {
                        Image(characters[idx])
                            .resizable()
                            .scaledToFit()
                            .transition(.scale.combined(with: .opacity))
                            .id(idx)
                    } else {
                        VStack(spacing: 10) {
                            Image(systemName: "questionmark.circle")
                                .font(.system(size: 44, weight: .light))
                                .foregroundColor(placeholderGray)
                            Text("Select a character below")
                                .font(.system(size: 13))
                                .foregroundColor(placeholderGray)
                        }
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 320)
                .padding(.horizontal, 24)
                .animation(.spring(response: 0.4, dampingFraction: 0.75), value: selectedIndex)

                Spacer().frame(height: 24)

                // MARK: - Slots
                HStack(spacing: 12) {
                    ForEach(characters.indices, id: \.self) { idx in
                        Button {
                            selectedIndex = idx
                        } label: {
                            ZStack {
                                RoundedRectangle(cornerRadius: 16)
                                    .fill(Color.white.opacity(0.7))
                                Image(characters[idx])
                                    .resizable()
                                    .scaledToFit()
                                    .padding(10)
                            }
                            .frame(maxWidth: .infinity)
                            .frame(height: 72)
                            .overlay(
                                RoundedRectangle(cornerRadius: 16)
                                    .stroke(
                                        selectedIndex == idx ? brandGreen : placeholderGray.opacity(0.4),
                                        lineWidth: selectedIndex == idx ? 2.5 : 1
                                    )
                            )
                            .shadow(
                                color: selectedIndex == idx ? brandGreen.opacity(0.3) : .clear,
                                radius: 6, x: 0, y: 3
                            )
                        }
                        .buttonStyle(.plain)
                        .animation(.easeInOut(duration: 0.2), value: selectedIndex)
                    }
                }
                .padding(.horizontal, 28)

                Spacer()

                // MARK: - Done Button
                HStack {
                    Spacer()
                    Button(action: {
                        if let idx = selectedIndex {
                            UserDefaults.standard.set(characters[idx], forKey: "selectedCharacter")
                            goToMain = true
                        }
                    }) {
                        Text("Done")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 120, height: 48)
                            .background(
                                RoundedRectangle(cornerRadius: 24)
                                    .fill(isDoneEnabled ? brandGreen : placeholderGray)
                            )
                            .shadow(color: brandGreen.opacity(isDoneEnabled ? 0.35 : 0), radius: 8, x: 0, y: 4)
                    }
                    .disabled(!isDoneEnabled)
                    .animation(.easeInOut(duration: 0.2), value: isDoneEnabled)
                }
                .padding(.horizontal, 28)
                .padding(.bottom, 40)
            }
        }
        .navigationBarBackButtonHidden(true)
        .navigationDestination(isPresented: $goToMain) {
            if let idx = selectedIndex {
                MainView(nickname: nickname, characterAsset: characters[idx])
            }
        }
    }
}

#Preview {
    CharacterSelectView(nickname: "Yeokyung")
}
