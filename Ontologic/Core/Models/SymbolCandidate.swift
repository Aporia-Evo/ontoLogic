// MARK: - SymbolCandidate.swift
// Represents a single recognition result candidate returned by the recognition engine.

import Foundation

/// A recognized symbol candidate with a confidence score.
struct SymbolCandidate: Identifiable, Codable, Hashable {
    let id: UUID
    /// Human-readable name of the symbol (e.g. "Om", "Yin Yang")
    let name: String
    /// Short category label (e.g. "Religious", "Geometric", "Alchemical")
    let category: SymbolCategory
    /// Confidence score in range [0, 1]
    let confidence: Double
    /// Optional thumbnail asset name or URL string
    let thumbnailName: String?

    init(
        id: UUID = UUID(),
        name: String,
        category: SymbolCategory,
        confidence: Double,
        thumbnailName: String? = nil
    ) {
        self.id = id
        self.name = name
        self.category = category
        self.confidence = confidence
        self.thumbnailName = thumbnailName
    }
}

// MARK: - SymbolCategory

enum SymbolCategory: String, Codable, CaseIterable {
    case religious    = "Religious"
    case geometric    = "Geometric"
    case alchemical   = "Alchemical"
    case astrological = "Astrological"
    case runic        = "Runic"
    case mathematical = "Mathematical"
    case cultural     = "Cultural"
    case nature       = "Nature"
    case unknown      = "Unknown"

    var displayName: String { rawValue }

    /// SF Symbol icon associated with category (for UI display)
    var iconName: String {
        switch self {
        case .religious:    return "person.crop.circle"
        case .geometric:    return "square.on.circle"
        case .alchemical:   return "flame"
        case .astrological: return "star"
        case .runic:        return "textformat"
        case .mathematical: return "function"
        case .cultural:     return "globe"
        case .nature:       return "leaf"
        case .unknown:      return "questionmark.circle"
        }
    }
}

// MARK: - Mock Data

extension SymbolCandidate {
    static let mockCandidates: [SymbolCandidate] = [
        SymbolCandidate(
            name: "Om (ॐ)",
            category: .religious,
            confidence: 0.94,
            thumbnailName: nil
        ),
        SymbolCandidate(
            name: "Yin Yang",
            category: .religious,
            confidence: 0.72,
            thumbnailName: nil
        ),
        SymbolCandidate(
            name: "Triquetra",
            category: .cultural,
            confidence: 0.61,
            thumbnailName: nil
        ),
        SymbolCandidate(
            name: "Pentagram",
            category: .geometric,
            confidence: 0.45,
            thumbnailName: nil
        ),
        SymbolCandidate(
            name: "Spiral",
            category: .geometric,
            confidence: 0.38,
            thumbnailName: nil
        )
    ]
}
