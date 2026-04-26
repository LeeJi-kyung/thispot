//
//  THISPOTApp.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

@main
struct MyApp: App {
    @State private var showSplash = true
    @State private var hasOnboarded: Bool = MyApp.checkOnboarded()

    static func checkOnboarded() -> Bool {
        let nick = UserDefaults.standard.string(forKey: "nickname") ?? ""
        let char = UserDefaults.standard.string(forKey: "selectedCharacter") ?? ""
        return !nick.isEmpty && !char.isEmpty
    }

    var body: some Scene {
        WindowGroup {
            if showSplash {
                SplashView()
                    .onAppear {
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                            withAnimation {
                                showSplash = false
                            }
                        }
                    }
            } else {
                NavigationStack {
                    if hasOnboarded {
                        MainView(
                            nickname: UserDefaults.standard.string(forKey: "nickname") ?? "",
                            characterAsset: UserDefaults.standard.string(forKey: "selectedCharacter") ?? ""
                        )
                    } else {
                        SignUpView()
                    }
                }
            }
        }
    }
}
