//
//  SplashView.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//
import SwiftUI

struct SplashView: View {
    @State private var scale: CGFloat = 0.6
    @State private var opacity: Double = 0.0

    var body: some View {
        ZStack {
            Color(red: 0.973, green: 0.965, blue: 0.953)
                .ignoresSafeArea()

            Image("logo")
                .resizable()
                .scaledToFit()
                .frame(width: 180, height: 180)
                .scaleEffect(scale)
                .opacity(opacity)
                .onAppear {
                    withAnimation(.spring(response: 0.6, dampingFraction: 0.6, blendDuration: 0)) {
                        scale = 1.0
                        opacity = 1.0
                    }
                }
        }
    }
}

#Preview {
    SplashView()
}
