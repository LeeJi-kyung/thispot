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
                    SignUpView()
                }
            }
        }
    }
}
