// MARK: - SettingsViewModel.swift

import Foundation
import Combine

final class SettingsViewModel: ObservableObject {

    // MARK: Persisted settings (backed by UserDefaults)

    @Published var strokeWidth: Double {
        didSet { UserDefaults.standard.set(strokeWidth, forKey: Keys.strokeWidth) }
    }

    @Published var hapticFeedbackEnabled: Bool {
        didSet { UserDefaults.standard.set(hapticFeedbackEnabled, forKey: Keys.hapticFeedback) }
    }

    @Published var autoRecognize: Bool {
        didSet { UserDefaults.standard.set(autoRecognize, forKey: Keys.autoRecognize) }
    }

    // MARK: Read-only info

    let appVersion: String = Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? "1.0"
    let buildNumber: String = Bundle.main.infoDictionary?["CFBundleVersion"] as? String ?? "1"

    // MARK: Keys

    private enum Keys {
        static let strokeWidth     = "onto_strokeWidth"
        static let hapticFeedback  = "onto_hapticFeedback"
        static let autoRecognize   = "onto_autoRecognize"
    }

    init() {
        let defaults = UserDefaults.standard
        self.strokeWidth            = defaults.object(forKey: Keys.strokeWidth) as? Double ?? 3.0
        self.hapticFeedbackEnabled  = defaults.object(forKey: Keys.hapticFeedback) as? Bool ?? true
        self.autoRecognize          = defaults.object(forKey: Keys.autoRecognize) as? Bool ?? false
    }

    func resetToDefaults() {
        strokeWidth            = 3.0
        hapticFeedbackEnabled  = true
        autoRecognize          = false
    }
}
