// MARK: - SymbolDetail.swift
// Full detail model for a symbol, used on the SymbolDetailView.

import Foundation

/// Full detail of a recognized symbol including meaning, origin and related symbols.
struct SymbolDetail: Identifiable, Codable {
    let id: UUID
    let name: String
    let category: SymbolCategory
    /// Short one-line description shown in list/card views
    let summary: String
    /// Full explanation (markdown-friendly)
    let meaning: String
    /// Historical or cultural origin text
    let origin: String
    /// Pronunciation guide, if applicable
    let pronunciation: String?
    /// Related symbol names
    let relatedSymbols: [String]
    /// Tags for search/filtering
    let tags: [String]
    /// Whether the user has marked this symbol as favourite
    var isFavourite: Bool

    init(
        id: UUID = UUID(),
        name: String,
        category: SymbolCategory,
        summary: String,
        meaning: String,
        origin: String,
        pronunciation: String? = nil,
        relatedSymbols: [String] = [],
        tags: [String] = [],
        isFavourite: Bool = false
    ) {
        self.id = id
        self.name = name
        self.category = category
        self.summary = summary
        self.meaning = meaning
        self.origin = origin
        self.pronunciation = pronunciation
        self.relatedSymbols = relatedSymbols
        self.tags = tags
        self.isFavourite = isFavourite
    }
}

// MARK: - Mock Data

extension SymbolDetail {
    static let mockOm = SymbolDetail(
        name: "Om (ॐ)",
        category: .religious,
        summary: "Sacred syllable of Hinduism, Buddhism and Jainism",
        meaning: """
        Om (also written Aum) is the most sacred sound and symbol in Hinduism, \
        representing the sound of the universe. It is considered the root mantra, \
        from which all other mantras emerge. In Buddhist traditions it appears at \
        the start of many mantras and reflects the essence of all existence.
        """,
        origin: """
        The earliest mention of Om is found in the Upanishads, the ancient Sanskrit \
        texts of Hindu philosophy, dating back to approximately 1000–800 BCE. The \
        syllable is described as the sound of Brahman, the ultimate reality. Its three \
        phonetic components (A-U-M) symbolise the states of waking, dreaming, and \
        deep sleep, while the silence after the sound represents pure consciousness.
        """,
        pronunciation: "ohm",
        relatedSymbols: ["Swastika", "Dharma Wheel", "Lotus", "Shri Yantra"],
        tags: ["hinduism", "buddhism", "jainism", "mantra", "meditation", "sacred"],
        isFavourite: false
    )

    static let mockYinYang = SymbolDetail(
        name: "Yin Yang",
        category: .religious,
        summary: "Taoist symbol representing the duality and balance of opposing forces",
        meaning: """
        The Yin-Yang symbol (Taijitu) represents the Taoist concept of dualism — how \
        seemingly opposite or contrary forces may actually be complementary. Yin \
        (dark/feminine/passive) and Yang (light/masculine/active) are not absolute \
        opposites but interdependent: each contains the seed of the other, shown by \
        the small circles within each half.
        """,
        origin: """
        The concept originates in ancient Chinese cosmology and philosophy. The earliest \
        known depictions date to the Shang Dynasty (1600–1046 BCE). The circular symbol \
        as commonly known today was elaborated by Song Dynasty philosopher Zhou Dunyi \
        (1017–1073 CE) in his work "Taijitu shuo" (Explanation of the Diagram of the \
        Supreme Ultimate).
        """,
        pronunciation: "yin yang",
        relatedSymbols: ["Bagua", "Taijitu", "Five Elements", "I Ching"],
        tags: ["taoism", "duality", "balance", "chinese", "philosophy"],
        isFavourite: false
    )

    static let mockTriquetra = SymbolDetail(
        name: "Triquetra",
        category: .cultural,
        summary: "Three-cornered Celtic knot symbolising trinity",
        meaning: """
        The Triquetra (Latin: three-cornered) is an ancient symbol consisting of three \
        interlocked arcs. It has been used to represent a wide variety of trinities: \
        in Celtic paganism the triple goddess (maiden/mother/crone); in Christianity \
        the Holy Trinity; in Norse mythology the three realms. Its continuous line \
        suggests eternity and interconnectedness.
        """,
        origin: """
        The Triquetra appears on Norse runic inscriptions and Celtic stone carvings from \
        as early as 500 BCE. It became widespread in Insular art (6th–8th century CE), \
        appearing in illuminated manuscripts such as the Book of Kells. It was later \
        adopted in early Christian iconography to symbolise the Father, Son and Holy Spirit.
        """,
        pronunciation: "try-KWEH-tra",
        relatedSymbols: ["Celtic Knot", "Triskelion", "Valknut", "Trinity Knot"],
        tags: ["celtic", "norse", "christianity", "trinity", "knot", "pagan"],
        isFavourite: false
    )

    /// Returns a mock detail for a given candidate name, falling back to Om.
    static func mock(for candidate: SymbolCandidate) -> SymbolDetail {
        switch candidate.name {
        case "Yin Yang":   return mockYinYang
        case "Triquetra":  return mockTriquetra
        default:           return mockOm
        }
    }
}
