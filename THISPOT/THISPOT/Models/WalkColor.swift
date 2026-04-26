//
//  WalkColor.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import SwiftUI

/// Rainbow palette used for the daily "Today's Color" walk theme.
/// Tones are slightly muted to sit nicely with the cream/sage app mood.
enum WalkColor: String, CaseIterable {
    case red, orange, yellow, green, blue, indigo, violet

    var displayName: String {
        rawValue.capitalized
    }

    var color: Color {
        switch self {
        case .red:    return Color(red: 0.92, green: 0.38, blue: 0.38)
        case .orange: return Color(red: 0.97, green: 0.62, blue: 0.30)
        case .yellow: return Color(red: 0.96, green: 0.80, blue: 0.30)
        case .green:  return Color(red: 0.50, green: 0.74, blue: 0.43)
        case .blue:   return Color(red: 0.36, green: 0.62, blue: 0.85)
        case .indigo: return Color(red: 0.39, green: 0.40, blue: 0.74)
        case .violet: return Color(red: 0.66, green: 0.45, blue: 0.78)
        }
    }

    /// Slightly darker variant for text-on-color or chip foregrounds when needed.
    var deepColor: Color {
        switch self {
        case .red:    return Color(red: 0.70, green: 0.20, blue: 0.20)
        case .orange: return Color(red: 0.80, green: 0.45, blue: 0.15)
        case .yellow: return Color(red: 0.70, green: 0.55, blue: 0.10)
        case .green:  return Color(red: 0.30, green: 0.52, blue: 0.25)
        case .blue:   return Color(red: 0.20, green: 0.42, blue: 0.66)
        case .indigo: return Color(red: 0.24, green: 0.25, blue: 0.55)
        case .violet: return Color(red: 0.46, green: 0.28, blue: 0.58)
        }
    }

    static func random() -> WalkColor {
        WalkColor.allCases.randomElement() ?? .green
    }
}
