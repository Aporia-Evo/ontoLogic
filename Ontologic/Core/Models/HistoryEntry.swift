// MARK: - HistoryEntry.swift
// Represents a past recognition session stored locally.

import Foundation

/// A record of a completed recognition session, persisted to local storage.
struct HistoryEntry: Identifiable, Codable {
    let id: UUID
    let date: Date
    /// The top candidate returned by the service
    let topCandidate: SymbolCandidate
    /// All candidates for replay in the results view
    let allCandidates: [SymbolCandidate]

    init(
        id: UUID = UUID(),
        date: Date = Date(),
        topCandidate: SymbolCandidate,
        allCandidates: [SymbolCandidate]
    ) {
        self.id = id
        self.date = date
        self.topCandidate = topCandidate
        self.allCandidates = allCandidates
    }
}

// MARK: - Mock Data

extension HistoryEntry {
    static let mockEntries: [HistoryEntry] = {
        let candidates = SymbolCandidate.mockCandidates
        return [
            HistoryEntry(
                date: Date().addingTimeInterval(-3600),
                topCandidate: candidates[0],
                allCandidates: candidates
            ),
            HistoryEntry(
                date: Date().addingTimeInterval(-86400),
                topCandidate: candidates[1],
                allCandidates: Array(candidates.suffix(3))
            ),
            HistoryEntry(
                date: Date().addingTimeInterval(-172800),
                topCandidate: candidates[2],
                allCandidates: [candidates[2], candidates[3]]
            )
        ]
    }()
}
