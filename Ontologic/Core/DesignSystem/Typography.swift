// MARK: - Typography.swift
// Centralised type scale for the Ontologic design system.

import SwiftUI

// MARK: - Font extensions

extension Font {
    // MARK: Display
    static let ontoDisplayLarge  = Font.system(size: 34, weight: .bold,   design: .rounded)
    static let ontoDisplayMedium = Font.system(size: 28, weight: .bold,   design: .rounded)

    // MARK: Headline
    static let ontoHeadlineLarge  = Font.system(size: 22, weight: .semibold, design: .rounded)
    static let ontoHeadlineMedium = Font.system(size: 18, weight: .semibold, design: .rounded)
    static let ontoHeadlineSmall  = Font.system(size: 16, weight: .semibold, design: .rounded)

    // MARK: Body
    static let ontoBodyLarge  = Font.system(size: 16, weight: .regular, design: .default)
    static let ontoBodyMedium = Font.system(size: 14, weight: .regular, design: .default)
    static let ontoBodySmall  = Font.system(size: 12, weight: .regular, design: .default)

    // MARK: Label
    static let ontoLabelLarge  = Font.system(size: 14, weight: .medium, design: .default)
    static let ontoLabelMedium = Font.system(size: 12, weight: .medium, design: .default)
    static let ontoLabelSmall  = Font.system(size: 10, weight: .medium, design: .default)

    // MARK: Mono (for confidence values / data)
    static let ontoMono = Font.system(size: 13, weight: .regular, design: .monospaced)
}

// MARK: - View modifiers for common text styles

struct OntoPrimaryTitleModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.ontoDisplayMedium)
            .foregroundColor(.ontoTextPrimary_fallback())
    }
}

struct OntoSectionHeaderModifier: ViewModifier {
    func body(content: Content) -> some View {
        content
            .font(.ontoHeadlineSmall)
            .foregroundColor(.ontoTextSecondary_fallback())
            .textCase(.uppercase)
            .tracking(0.8)
    }
}

extension View {
    func ontoPrimaryTitle()  -> some View { modifier(OntoPrimaryTitleModifier()) }
    func ontoSectionHeader() -> some View { modifier(OntoSectionHeaderModifier()) }
}
