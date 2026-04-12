// MARK: - ResultsViewModel.swift

import Foundation
import Combine

final class ResultsViewModel: ObservableObject {

    @Published private(set) var candidates: [SymbolCandidate] = []
    @Published var selectedCandidate: SymbolCandidate? = nil

    let processingTimeMs: Double?
    let modelVersion: String?

    init(response: RecognitionResponse) {
        self.candidates      = response.candidates
        self.processingTimeMs = response.processingTimeMs
        self.modelVersion    = response.modelVersion
        self.selectedCandidate = response.topCandidate
    }
}
