// MARK: - OCard.swift
// Generic card container and symbol-candidate card.

import SwiftUI

// MARK: - Base card modifier

struct OCardModifier: ViewModifier {
    var cornerRadius: CGFloat = 16

    func body(content: Content) -> some View {
        content
            .background(Color.ontoSurface_fallback())
            .clipShape(RoundedRectangle(cornerRadius: cornerRadius, style: .continuous))
            .shadow(color: .black.opacity(0.25), radius: 8, x: 0, y: 4)
    }
}

extension View {
    func ontoCard(cornerRadius: CGFloat = 16) -> some View {
        modifier(OCardModifier(cornerRadius: cornerRadius))
    }
}

// MARK: - CandidateCard

/// Card showing a symbol candidate with name, category badge, and confidence bar.
struct CandidateCard: View {
    let candidate: SymbolCandidate
    let isHighlighted: Bool
    let onTap: () -> Void

    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 14) {
                // Rank indicator / thumbnail placeholder
                ZStack {
                    Circle()
                        .fill(Color.ontoPrimary_fallback().opacity(0.15))
                        .frame(width: 48, height: 48)
                    Image(systemName: candidate.category.iconName)
                        .font(.system(size: 20))
                        .foregroundColor(.ontoPrimary_fallback())
                }

                // Name + category
                VStack(alignment: .leading, spacing: 4) {
                    Text(candidate.name)
                        .font(.ontoHeadlineSmall)
                        .foregroundColor(.ontoTextPrimary_fallback())
                        .lineLimit(1)

                    CategoryBadge(category: candidate.category)
                }

                Spacer()

                // Confidence
                VStack(alignment: .trailing, spacing: 4) {
                    Text(String(format: "%.0f%%", candidate.confidence * 100))
                        .font(.ontoMono)
                        .foregroundColor(Color.confidenceColor(candidate.confidence))

                    ConfidenceBar(value: candidate.confidence)
                        .frame(width: 60, height: 4)
                }
            }
            .padding(14)
            .ontoCard()
            .overlay(
                RoundedRectangle(cornerRadius: 16, style: .continuous)
                    .stroke(
                        isHighlighted ? Color.ontoPrimary_fallback() : Color.clear,
                        lineWidth: 2
                    )
            )
        }
        .buttonStyle(.plain)
        .accessibilityLabel("\(candidate.name), \(candidate.category.displayName), \(Int(candidate.confidence * 100)) percent confidence")
    }
}

// MARK: - ConfidenceBar

struct ConfidenceBar: View {
    let value: Double   // 0…1

    var body: some View {
        GeometryReader { geo in
            ZStack(alignment: .leading) {
                Capsule()
                    .fill(Color.ontoSurfaceSecond_fallback())
                Capsule()
                    .fill(Color.confidenceColor(value))
                    .frame(width: geo.size.width * value)
            }
        }
    }
}

// MARK: - Previews

#Preview("CandidateCard") {
    VStack(spacing: 12) {
        ForEach(SymbolCandidate.mockCandidates) { c in
            CandidateCard(
                candidate: c,
                isHighlighted: c == SymbolCandidate.mockCandidates.first,
                onTap: {}
            )
        }
    }
    .padding()
    .background(Color.ontoBackground_fallback())
}
