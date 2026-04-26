//
//  WalkTracker.swift
//  THISPOT
//
//  Created by 송여경 on 4/26/26.
//

import Foundation
import CoreLocation
import Combine

final class WalkTracker: NSObject, ObservableObject {
    @Published private(set) var distanceMeters: Double = 0
    @Published private(set) var path: [CLLocationCoordinate2D] = []
    @Published private(set) var isTracking: Bool = false

    var distanceKm: Double { distanceMeters / 1000 }

    private let manager = CLLocationManager()
    private var lastLocation: CLLocation?

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.distanceFilter = 5
        manager.activityType = .fitness
    }

    func start() {
        isTracking = true
        switch manager.authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways:
            manager.startUpdatingLocation()
        default:
            break
        }
    }

    func stop() {
        isTracking = false
        manager.stopUpdatingLocation()
    }
}

extension WalkTracker: CLLocationManagerDelegate {
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedWhenInUse, .authorizedAlways:
            if isTracking { manager.startUpdatingLocation() }
        default:
            break
        }
    }

    func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        for loc in locations {
            // Filter out noisy / cached fixes
            guard loc.horizontalAccuracy > 0, loc.horizontalAccuracy < 30 else { continue }
            guard abs(loc.timestamp.timeIntervalSinceNow) < 5 else { continue }

            if let last = lastLocation {
                let delta = loc.distance(from: last)
                // Skip jitter under 2m, and big jumps that imply GPS drift
                guard delta >= 2, delta < 80 else {
                    lastLocation = loc
                    continue
                }
                DispatchQueue.main.async {
                    self.distanceMeters += delta
                    self.path.append(loc.coordinate)
                }
            } else {
                DispatchQueue.main.async {
                    self.path.append(loc.coordinate)
                }
            }
            lastLocation = loc
        }
    }
}
