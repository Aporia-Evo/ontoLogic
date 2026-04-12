// MARK: - StatusBadge.swift
// Pill-shaped badges for category, status, and tags.

import SwiftUI

// MARK: - CategoryBadge

/// Displays the symbol category as a coloured pill.
struct CategoryBadge: View {
    let category: SymbolCategory

    var body: some View {
        Text(category.displayName)
            .font(.ontoLabelSmall)
            .foregroundColor(.white)
            .padding(.horizontal, 8)
            .padding(.vertical, 3)
            .background(badgeColor)
            .clipShape(Capsule())
    }

    private var badgeColor: Color {
        switch category {
        case .religious:    return Color(hex: "#6366F1") ?? .indigo
        case .geometric:    return Color(hex: "#8B5CF6") ?? .purple
        case .alchemical:   return Color(hex: "#EF4444") ?? .red
        case .astrological: return Color(hex: "#0EA5E9") ?? .cyan
        case .runic:        return Color(hex: "#10B981") ?? .green
        case .mathematical: return Color(hex: "#F59E0B") ?? .orange
        case .cultural:     return Color(hex: "#EC4899") ?? .pink
        case .nature:       return Color(hex: "#22C55E") ?? .green
        case .unknown:      return Color.ontoTextTertiary_fallback()
        }
    }
}

// MARK: - TagBadge

/// A plain tag chip, used in SymbolDetail.
struct TagBadge: View {
    let text: String

    var body: some View {
        Text("#\(text)")
            .font(.ontoLabelSmall)
            .foregroundColor(.ontoTextSecondary_fallback())
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.ontoSurfaceSecond_fallback())
            .clipShape(Capsule())
    }
}

// MARK: - ConfidenceBadge

/// Inline confidence percentage badge.
struct ConfidenceBadge: View {
    let score: Double

    var body: some View {
        Text(String(format: "%.0f%%", score * 100))
            .font(.ontoLabelMedium)
            .foregroundColor(Color.confidenceColor(score))
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(Color.confidenceColor(score).opacity(0.15))
            .clipShape(Capsule())
    }
}

// MARK: - Previews

#Preview("Badges") {
    ScrollView {
        VStack(alignment: .leading, spacing: 20) {
            Text("Category Badges").ontoSectionHeader()
            FlowLayout(spacing: 8) {
                ForEach(SymbolCategory.allCases, id: \.self) { cat in
                    CategoryBadge(category: cat)
                }
            }

            Text("Tag Badges").ontoSectionHeader()
            FlowLayout(spacing: 8) {
                ForEach(["hinduism", "meditation", "sacred", "mantra", "ancient"], id: \.self) { tag in
                    TagBadge(text: tag)
                }
            }

            Text("Confidence Badges").ontoSectionHeader()
            HStack(spacing: 8) {
                ConfidenceBadge(score: 0.94)
                ConfidenceBadge(score: 0.6)
                ConfidenceBadge(score: 0.3)
            }
        }
        .padding()
    }
    .background(Color.ontoBackground_fallback())
}

// MARK: - FlowLayout helper (wrapping HStack)

/// A simple wrapping layout for badge chips.
struct FlowLayout: Layout {
    var spacing: CGFloat = 8

    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        layout(subviews: subviews, in: proposal.width ?? 320).size
    }

    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = layout(subviews: subviews, in: bounds.width)
        for (index, frame) in result.frames.enumerated() {
            subviews[index].place(
                at: CGPoint(x: bounds.minX + frame.minX, y: bounds.minY + frame.minY),
                proposal: ProposedViewSize(frame.size)
            )
        }
    }

    private func layout(subviews: Subviews, in width: CGFloat) -> (size: CGSize, frames: [CGRect]) {
        var frames: [CGRect] = []
        var x: CGFloat = 0
        var y: CGFloat = 0
        var rowHeight: CGFloat = 0
        var totalHeight: CGFloat = 0

        for subview in subviews {
            let size = subview.sizeThatFits(.unspecified)
            if x + size.width > width && x > 0 {
                y += rowHeight + spacing
                x = 0
                rowHeight = 0
            }
            frames.append(CGRect(origin: CGPoint(x: x, y: y), size: size))
            x += size.width + spacing
            rowHeight = max(rowHeight, size.height)
            totalHeight = y + rowHeight
        }

        return (CGSize(width: width, height: totalHeight), frames)
    }
}
