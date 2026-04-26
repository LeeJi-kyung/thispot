//
//  WalkReport.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import Foundation

struct WalkReport {
    let id: UUID
    let color: WalkColor
    let distanceMeters: Double
    let durationSec: Int
    let photoCount: Int
    let endedAt: Date

    var distanceKm: Double { distanceMeters / 1000 }

    /// Rough estimate using ~55 kcal per km for an average walker.
    /// Replace with a real model when we have user weight / pace.
    var calories: Int {
        max(1, Int((distanceKm * 55).rounded()))
    }

    var durationText: String {
        let minutes = max(1, durationSec / 60)
        return "\(minutes) min"
    }
}
