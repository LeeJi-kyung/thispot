//
//  SignUpView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

struct SignUpView: View {
    @State private var nickname: String = ""
    @State private var goToCharacter: Bool = false
    @FocusState private var isNicknameFocused: Bool

    private let backgroundCream = Color(red: 0.973, green: 0.965, blue: 0.953)
    private let brandGreen      = Color(red: 0.502, green: 0.651, blue: 0.388)
    private let brandBrown      = Color(red: 0.600, green: 0.420, blue: 0.220)
    private let textDark        = Color(red: 0.20, green: 0.20, blue: 0.20)
    private let placeholderGray = Color(red: 0.70, green: 0.70, blue: 0.70)

    var isNextEnabled: Bool { !nickname.trimmingCharacters(in: .whitespaces).isEmpty }

    var body: some View {
        ZStack {
            backgroundCream.ignoresSafeArea()

            VStack(alignment: .leading, spacing: 0) {

                // MARK: - Title
                Text("Sign Up")
                    .font(.system(size: 28, weight: .bold))
                    .foregroundColor(textDark)
                    .padding(.top, 56)
                    .padding(.horizontal, 28)

                Spacer().frame(height: 48)

                // MARK: - Nickname Field
                VStack(alignment: .leading, spacing: 8) {
                    Text("Nickname")
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(brandGreen)

                    TextField("Enter your nickname", text: $nickname)
                        .font(.system(size: 16))
                        .foregroundColor(textDark)
                        .focused($isNicknameFocused)
                        .padding(.vertical, 14)
                        .padding(.horizontal, 16)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Color.white.opacity(0.7))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(isNicknameFocused ? brandGreen : placeholderGray.opacity(0.5), lineWidth: 1.5)
                        )
                        .autocorrectionDisabled()
                }
                .padding(.horizontal, 28)

                Spacer()

                // MARK: - Next Button
                HStack {
                    Spacer()
                    Button(action: {
                        let trimmed = nickname.trimmingCharacters(in: .whitespaces)
                        if !trimmed.isEmpty {
                            UserDefaults.standard.set(trimmed, forKey: "nickname")
                            goToCharacter = true
                        }
                    }) {
                        Text("Next")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.white)
                            .frame(width: 120, height: 48)
                            .background(
                                RoundedRectangle(cornerRadius: 24)
                                    .fill(isNextEnabled ? brandGreen : placeholderGray)
                            )
                            .shadow(color: brandGreen.opacity(isNextEnabled ? 0.35 : 0), radius: 8, x: 0, y: 4)
                    }
                    .disabled(!isNextEnabled)
                    .animation(.easeInOut(duration: 0.2), value: isNextEnabled)
                }
                .padding(.horizontal, 28)
                .padding(.bottom, 40)
            }
        }
        .onTapGesture { isNicknameFocused = false }
        .navigationDestination(isPresented: $goToCharacter) {
            CharacterSelectView(nickname: nickname.trimmingCharacters(in: .whitespaces))
        }
    }
}

#Preview {
    SignUpView()
}
