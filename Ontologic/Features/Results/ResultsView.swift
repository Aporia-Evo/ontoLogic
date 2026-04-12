// MARK: - ResultsView.swift
// Shows the list of recognition candidates ordered by confidence.

import SwiftUI

struct ResultsView: View {

    @StateObject var viewModel: ResultsViewModel

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            if viewModel.candidates.isEmpty {
                EmptyStateView(
                    icon: "questionmark.circle",
                    title: "No Symbols Found",
                    message: "We couldn't recognise the drawing. Try drawing more clearly or with fewer strokes."
                )
            } else {
                ScrollView {
                    VStack(spacing: 12) {
                        // Summary header
                        summaryHeader

                        // Candidate list
                        ForEach(Array(viewModel.candidates.enumerated()), id: \.element.id) { index, candidate in
                            NavigationLink(value: candidate) {
                                CandidateCard(
                                    candidate: candidate,
                                    isHighlighted: candidate.id == viewModel.selectedCandidate?.id,
                                    onTap: { viewModel.selectedCandidate = candidate }
                                )
                            }
                            .buttonStyle(.plain)
                            .accessibilityHint("Opens detail view for \(candidate.name)")
                        }

                        // Metadata footer
                        metaFooter
                    }
                    .padding(16)
                    .padding(.bottom, 24)
                }
            }
        }
        .navigationTitle("Results")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(for: SymbolCandidate.self) { candidate in
            // Injected via parent NavigationStack if needed;
            // here we provide a standalone fallback using mock service.
            SymbolDetailView(
                viewModel: SymbolDetailViewModel(
                    candidate: candidate,
                    service: MockRecognitionService.preview,
                    favouritesRepo: UserDefaultsFavouritesRepository()
                )
            )
        }
    }

    // MARK: Subviews

    private var summaryHeader: some View {
        VStack(spacing: 6) {
            Text("\(viewModel.candidates.count) Candidates Found")
                .font(.ontoHeadlineLarge)
                .foregroundColor(.ontoTextPrimary_fallback())

            if let top = viewModel.candidates.first {
                HStack(spacing: 6) {
                    Text("Best match:")
                        .font(.ontoBodyMedium)
                        .foregroundColor(.ontoTextSecondary_fallback())
                    Text(top.name)
                        .font(.ontoBodyMedium)
                        .foregroundColor(.ontoPrimary_fallback())
                    ConfidenceBadge(score: top.confidence)
                }
            }
        }
        .frame(maxWidth: .infinity)
        .padding(16)
        .ontoCard()
    }

    private var metaFooter: some View {
        VStack(spacing: 4) {
            if let ms = viewModel.processingTimeMs {
                Text(String(format: "Processed in %.0f ms", ms))
                    .font(.ontoLabelSmall)
                    .foregroundColor(.ontoTextTertiary_fallback())
            }
            if let version = viewModel.modelVersion {
                Text("Model: \(version)")
                    .font(.ontoLabelSmall)
                    .foregroundColor(.ontoTextTertiary_fallback())
            }
        }
        .padding(.top, 8)
    }
}

// MARK: - Preview

#Preview("With results") {
    NavigationStack {
        ResultsView(viewModel: ResultsViewModel(response: .mockResponse))
    }
    .preferredColorScheme(.dark)
}

#Preview("Empty") {
    NavigationStack {
        ResultsView(viewModel: ResultsViewModel(response: .mockEmptyResponse))
    }
    .preferredColorScheme(.dark)
}
