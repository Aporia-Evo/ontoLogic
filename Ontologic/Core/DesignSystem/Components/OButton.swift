// MARK: - OButton.swift
// Reusable button component for the Ontologic design system.

import SwiftUI

// MARK: - Style variants

enum OButtonStyle {
    case primary
    case secondary
    case destructive
    case ghost
}

// MARK: - OButton

/// A styled button conforming to the Ontologic design system.
struct OButton: View {
    let title: String
    let icon: String?
    let style: OButtonStyle
    let isLoading: Bool
    let isDisabled: Bool
    let action: () -> Void

    init(
        _ title: String,
        icon: String? = nil,
        style: OButtonStyle = .primary,
        isLoading: Bool = false,
        isDisabled: Bool = false,
        action: @escaping () -> Void
    ) {
        self.title = title
        self.icon = icon
        self.style = style
        self.isLoading = isLoading
        self.isDisabled = isDisabled
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            HStack(spacing: 8) {
                if isLoading {
                    ProgressView()
                        .progressViewStyle(.circular)
                        .tint(foregroundColor)
                        .scaleEffect(0.8)
                } else if let icon {
                    Image(systemName: icon)
                        .font(.system(size: 15, weight: .semibold))
                }
                Text(title)
                    .font(.ontoHeadlineSmall)
            }
            .padding(.horizontal, 20)
            .padding(.vertical, 13)
            .frame(maxWidth: .infinity)
            .background(backgroundColor)
            .foregroundColor(foregroundColor)
            .clipShape(RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay(
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .stroke(borderColor, lineWidth: borderWidth)
            )
        }
        .disabled(isDisabled || isLoading)
        .opacity((isDisabled || isLoading) ? 0.5 : 1)
        .accessibilityLabel(title)
        .accessibilityHint(isLoading ? "Loading, please wait" : "")
    }

    // MARK: Style helpers

    private var backgroundColor: Color {
        switch style {
        case .primary:     return .ontoPrimary_fallback()
        case .secondary:   return .ontoSurfaceSecond_fallback()
        case .destructive: return .ontoDestructive_fallback()
        case .ghost:       return .clear
        }
    }

    private var foregroundColor: Color {
        switch style {
        case .primary, .destructive: return .white
        case .secondary:             return .ontoTextPrimary_fallback()
        case .ghost:                 return .ontoPrimary_fallback()
        }
    }

    private var borderColor: Color {
        switch style {
        case .ghost: return .ontoPrimary_fallback().opacity(0.4)
        default:     return .clear
        }
    }

    private var borderWidth: CGFloat {
        style == .ghost ? 1.5 : 0
    }
}

// MARK: - Icon-only button

/// A compact circular icon button.
struct OIconButton: View {
    let icon: String
    let accessibilityLabel: String
    let style: OButtonStyle
    let action: () -> Void

    init(
        _ icon: String,
        accessibilityLabel: String,
        style: OButtonStyle = .secondary,
        action: @escaping () -> Void
    ) {
        self.icon = icon
        self.accessibilityLabel = accessibilityLabel
        self.style = style
        self.action = action
    }

    var body: some View {
        Button(action: action) {
            Image(systemName: icon)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(iconColor)
                .frame(width: 44, height: 44)
                .background(backgroundColor)
                .clipShape(Circle())
        }
        .accessibilityLabel(accessibilityLabel)
    }

    private var backgroundColor: Color {
        switch style {
        case .primary:     return .ontoPrimary_fallback()
        case .destructive: return .ontoDestructive_fallback()
        default:           return .ontoSurfaceSecond_fallback()
        }
    }

    private var iconColor: Color {
        switch style {
        case .primary, .destructive: return .white
        default:                     return .ontoTextPrimary_fallback()
        }
    }
}

// MARK: - Previews

#Preview("OButton styles") {
    VStack(spacing: 16) {
        OButton("Recognize Symbol", icon: "wand.and.stars", style: .primary) {}
        OButton("Clear Canvas",     icon: "trash",          style: .destructive) {}
        OButton("See Details",      icon: "info.circle",    style: .secondary) {}
        OButton("Skip",                                      style: .ghost) {}
        OButton("Loading…",                                  style: .primary, isLoading: true) {}
        OButton("Disabled",                                  style: .primary, isDisabled: true) {}
    }
    .padding()
    .background(Color.ontoBackground_fallback())
}
