//
//  WeatherManager.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import Foundation
import CoreLocation
import WeatherKit

@MainActor
final class WeatherManager: ObservableObject {
    // Defaults double as mock fallback when WeatherKit is unavailable
    // (capability not yet enabled, no network, propagation delay, etc.)
    @Published var symbol: String = "☀️"
    @Published var temperatureText: String = "22°"

    private let service = WeatherService.shared

    func fetch(for location: CLLocation) async {
        do {
            let weather = try await service.weather(for: location)
            self.symbol = Self.emoji(for: weather.currentWeather.symbolName)
            let celsius = weather.currentWeather.temperature.converted(to: .celsius)
            self.temperatureText = "\(Int(celsius.value.rounded()))°"
        } catch {
            // Keep current values (initial mock or last good) so the chip never goes blank.
            #if DEBUG
            print("[WeatherManager] fetch failed, falling back to mock — \(error)")
            #endif
        }
    }

    // Apple SF Symbol name → emoji
    private static func emoji(for symbolName: String) -> String {
        let s = symbolName.lowercased()
        if s.contains("bolt")        { return "⛈" }
        if s.contains("snow")        { return "❄️" }
        if s.contains("sleet") || s.contains("hail") { return "🌨" }
        if s.contains("rain") || s.contains("drizzle") { return "🌧" }
        if s.contains("fog") || s.contains("mist") || s.contains("haze") { return "🌫" }
        if s.contains("wind")        { return "💨" }
        if s.contains("cloud.sun") || s.contains("sun.cloud") { return "🌤" }
        if s.contains("cloud.moon")  { return "☁️" }
        if s.contains("cloud")       { return "☁️" }
        if s.contains("moon")        { return "🌙" }
        if s.contains("sun")         { return "☀️" }
        return "🌤"
    }
}
