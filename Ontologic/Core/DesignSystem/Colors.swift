// MARK: - Colors.swift
// Centralised colour palette for the Ontologic design system.
// All colours are defined as SwiftUI Color extensions to support
// dark-mode adaptation and future theming.

import SwiftUI

extension Color {

    // MARK: Brand

    /// Primary brand accent — deep indigo
    static let ontoPrimary       = Color("OntoPrimary",   bundle: nil)
    /// Secondary accent — teal/cyan
    static let ontoSecondary     = Color("OntoSecondary", bundle: nil)
    /// Destructive / error red
    static let ontoDestructive   = Color("OntoDestructive", bundle: nil)

    // MARK: Backgrounds

    static let ontoBackground    = Color("OntoBackground",    bundle: nil)
    static let ontoSurface       = Color("OntoSurface",       bundle: nil)
    static let ontoSurfaceSecond = Color("OntoSurfaceSecond", bundle: nil)

    // MARK: Text

    static let ontoTextPrimary   = Color("OntoTextPrimary",   bundle: nil)
    static let ontoTextSecondary = Color("OntoTextSecondary", bundle: nil)
    static let ontoTextTertiary  = Color("OntoTextTertiary",  bundle: nil)

    // MARK: Semantic

    static let ontoSuccess       = Color("OntoSuccess", bundle: nil)
    static let ontoWarning       = Color("OntoWarning", bundle: nil)
}

// MARK: - Fallback palette (used when Asset Catalog colours are not present)
// These hex-based colours provide a consistent appearance in Previews and
// targets that haven't yet added the Asset Catalog.

extension Color {
    /// Resolves to the named asset when available, otherwise falls back to the
    /// supplied hex value. Allows previews to render correctly without the full
    /// Xcode Asset Catalog.
    static func ontoPrimary_fallback()       -> Color { Color(hex: "#4F46E5") ?? .indigo }
    static func ontoSecondary_fallback()     -> Color { Color(hex: "#0EA5E9") ?? .cyan }
    static func ontoDestructive_fallback()   -> Color { Color(hex: "#EF4444") ?? .red }
    static func ontoBackground_fallback()    -> Color { Color(hex: "#0F0F1A") ?? Color(.systemBackground) }
    static func ontoSurface_fallback()       -> Color { Color(hex: "#1A1A2E") ?? Color(.secondarySystemBackground) }
    static func ontoSurfaceSecond_fallback() -> Color { Color(hex: "#252540") ?? Color(.tertiarySystemBackground) }
    static func ontoTextPrimary_fallback()   -> Color { Color(hex: "#F1F5F9") ?? .primary }
    static func ontoTextSecondary_fallback() -> Color { Color(hex: "#94A3B8") ?? .secondary }
    static func ontoTextTertiary_fallback()  -> Color { Color(hex: "#475569") ?? .gray }
    static func ontoSuccess_fallback()       -> Color { Color(hex: "#22C55E") ?? .green }
    static func ontoWarning_fallback()       -> Color { Color(hex: "#F59E0B") ?? .orange }
}

// MARK: - Hex initialiser

extension Color {
    /// Creates a Color from a CSS hex string (#RRGGBB or #RRGGBBAA).
    init?(hex: String) {
        let stripped = hex.trimmingCharacters(in: CharacterSet(charactersIn: "#"))
        let scanner = Scanner(string: stripped)
        var rgbValue: UInt64 = 0
        guard scanner.scanHexInt64(&rgbValue) else { return nil }

        let r, g, b, a: Double
        switch stripped.count {
        case 6:
            r = Double((rgbValue >> 16) & 0xFF) / 255
            g = Double((rgbValue >>  8) & 0xFF) / 255
            b = Double( rgbValue        & 0xFF) / 255
            a = 1.0
        case 8:
            r = Double((rgbValue >> 24) & 0xFF) / 255
            g = Double((rgbValue >> 16) & 0xFF) / 255
            b = Double((rgbValue >>  8) & 0xFF) / 255
            a = Double( rgbValue        & 0xFF) / 255
        default:
            return nil
        }
        self.init(.sRGB, red: r, green: g, blue: b, opacity: a)
    }
}

// MARK: - Confidence colour helper

extension Color {
    /// Returns a semantic colour for a confidence score in [0, 1].
    static func confidenceColor(_ score: Double) -> Color {
        switch score {
        case 0.75...: return .ontoSuccess_fallback()
        case 0.45...: return .ontoWarning_fallback()
        default:      return .ontoTextSecondary_fallback()
        }
    }
}
