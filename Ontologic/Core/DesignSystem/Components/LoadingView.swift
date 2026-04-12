// MARK: - LoadingView.swift
// Standardised loading and empty-state placeholder views.

import SwiftUI

// MARK: - LoadingView

/// Full-screen loading overlay with animated indicator.
struct LoadingView: View {
    var message: String = "Analysing your symbol…"

    var body: some View {
        VStack(spacing: 20) {
            ZStack {
                Circle()
                    .stroke(Color.ontoPrimary_fallback().opacity(0.2), lineWidth: 4)
                    .frame(width: 56, height: 56)

                Circle()
                    .trim(from: 0, to: 0.7)
                    .stroke(
                        AngularGradient(
                            colors: [.ontoPrimary_fallback(), .ontoSecondary_fallback()],
                            center: .center
                        ),
                        style: StrokeStyle(lineWidth: 4, lineCap: .round)
                    )
                    .frame(width: 56, height: 56)
                    .rotationEffect(.degrees(-90))
                    .modifier(SpinModifier())
            }

            Text(message)
                .font(.ontoBodyMedium)
                .foregroundColor(.ontoTextSecondary_fallback())
                .multilineTextAlignment(.center)
        }
        .padding(32)
        .accessibilityElement(children: .combine)
        .accessibilityLabel("Loading: \(message)")
    }
}

// MARK: - Spin animation modifier

private struct SpinModifier: ViewModifier {
    @State private var angle: Double = 0

    func body(content: Content) -> some View {
        content
            .rotationEffect(.degrees(angle))
            .onAppear {
                withAnimation(.linear(duration: 1).repeatForever(autoreverses: false)) {
                    angle = 360
                }
            }
    }
}

// MARK: - EmptyStateView

/// Generic empty-state placeholder.
struct EmptyStateView: View {
    let icon: String
    let title: String
    let message: String
    var actionTitle: String? = nil
    var action: (() -> Void)? = nil

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 48, weight: .light))
                .foregroundColor(.ontoTextTertiary_fallback())

            Text(title)
                .font(.ontoHeadlineMedium)
                .foregroundColor(.ontoTextPrimary_fallback())

            Text(message)
                .font(.ontoBodyMedium)
                .foregroundColor(.ontoTextSecondary_fallback())
                .multilineTextAlignment(.center)

            if let actionTitle, let action {
                OButton(actionTitle, style: .secondary, action: action)
                    .frame(maxWidth: 220)
            }
        }
        .padding(32)
        .accessibilityElement(children: .combine)
    }
}

// MARK: - ErrorView

/// Displays an error with a retry action.
struct ErrorView: View {
    let error: Error
    var retryAction: (() -> Void)? = nil

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 48, weight: .light))
                .foregroundColor(.ontoDestructive_fallback())

            Text("Something went wrong")
                .font(.ontoHeadlineMedium)
                .foregroundColor(.ontoTextPrimary_fallback())

            Text(error.localizedDescription)
                .font(.ontoBodyMedium)
                .foregroundColor(.ontoTextSecondary_fallback())
                .multilineTextAlignment(.center)

            if let retryAction {
                OButton("Try Again", icon: "arrow.clockwise", style: .primary, action: retryAction)
                    .frame(maxWidth: 220)
            }
        }
        .padding(32)
    }
}

// MARK: - Previews

#Preview("LoadingView") {
    ZStack {
        Color.ontoBackground_fallback().ignoresSafeArea()
        LoadingView()
    }
}

#Preview("EmptyStateView") {
    ZStack {
        Color.ontoBackground_fallback().ignoresSafeArea()
        EmptyStateView(
            icon: "clock.arrow.circlepath",
            title: "No History Yet",
            message: "Draw a symbol and recognise it to see results here.",
            actionTitle: "Draw a Symbol",
            action: {}
        )
    }
}

#Preview("ErrorView") {
    ZStack {
        Color.ontoBackground_fallback().ignoresSafeArea()
        ErrorView(error: RecognitionError.networkUnavailable, retryAction: {})
    }
}
