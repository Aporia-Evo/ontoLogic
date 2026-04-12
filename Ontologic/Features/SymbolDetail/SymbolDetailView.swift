// MARK: - SymbolDetailView.swift

import SwiftUI

struct SymbolDetailView: View {

    @StateObject var viewModel: SymbolDetailViewModel

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            switch viewModel.state {
            case .loading:
                LoadingView(message: "Loading symbol details…")

            case .error(let error):
                ErrorView(error: error) {
                    Task { await viewModel.loadIfNeeded() }
                }

            case .loaded(let detail):
                detailContent(detail)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button {
                    viewModel.toggleFavourite()
                } label: {
                    Image(systemName: viewModel.isFavourite ? "star.fill" : "star")
                        .foregroundColor(viewModel.isFavourite ? .yellow : .ontoTextSecondary_fallback())
                }
                .accessibilityLabel(viewModel.isFavourite ? "Remove from favourites" : "Add to favourites")
            }
        }
        .task {
            await viewModel.loadIfNeeded()
        }
    }

    // MARK: Detail content

    @ViewBuilder
    private func detailContent(_ detail: SymbolDetail) -> some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {

                // Hero
                heroSection(detail)

                // Meaning
                section(title: "Meaning") {
                    Text(detail.meaning)
                        .font(.ontoBodyLarge)
                        .foregroundColor(.ontoTextSecondary_fallback())
                }

                // Origin
                section(title: "Origin") {
                    Text(detail.origin)
                        .font(.ontoBodyLarge)
                        .foregroundColor(.ontoTextSecondary_fallback())
                }

                // Related symbols
                if !detail.relatedSymbols.isEmpty {
                    section(title: "Related Symbols") {
                        FlowLayout(spacing: 8) {
                            ForEach(detail.relatedSymbols, id: \.self) { name in
                                Text(name)
                                    .font(.ontoLabelMedium)
                                    .foregroundColor(.ontoTextPrimary_fallback())
                                    .padding(.horizontal, 10)
                                    .padding(.vertical, 5)
                                    .background(Color.ontoSurfaceSecond_fallback())
                                    .clipShape(Capsule())
                            }
                        }
                    }
                }

                // Tags
                if !detail.tags.isEmpty {
                    section(title: "Tags") {
                        FlowLayout(spacing: 8) {
                            ForEach(detail.tags, id: \.self) { tag in
                                TagBadge(text: tag)
                            }
                        }
                    }
                }
            }
            .padding(20)
            .padding(.bottom, 32)
        }
    }

    // MARK: Hero section

    private func heroSection(_ detail: SymbolDetail) -> some View {
        HStack(spacing: 20) {
            ZStack {
                Circle()
                    .fill(
                        LinearGradient(
                            colors: [.ontoPrimary_fallback().opacity(0.3), .ontoSecondary_fallback().opacity(0.15)],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
                    .frame(width: 80, height: 80)
                Image(systemName: detail.category.iconName)
                    .font(.system(size: 34))
                    .foregroundColor(.ontoPrimary_fallback())
            }

            VStack(alignment: .leading, spacing: 6) {
                Text(detail.name)
                    .font(.ontoDisplayMedium)
                    .foregroundColor(.ontoTextPrimary_fallback())

                if let pronunciation = detail.pronunciation {
                    Text("/\(pronunciation)/")
                        .font(.ontoBodySmall)
                        .foregroundColor(.ontoTextTertiary_fallback())
                        .italic()
                }

                CategoryBadge(category: detail.category)
            }

            Spacer()
        }
        .padding(16)
        .ontoCard()
    }

    // MARK: Section builder

    private func section<Content: View>(title: String, @ViewBuilder content: () -> Content) -> some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(title)
                .ontoSectionHeader()
            content()
        }
    }
}

// MARK: - Hashable conformance for navigation

extension SymbolDetail: Hashable {
    static func == (lhs: SymbolDetail, rhs: SymbolDetail) -> Bool { lhs.id == rhs.id }
    func hash(into hasher: inout Hasher) { hasher.combine(id) }
}

// MARK: - Preview

#Preview("Symbol Detail — Loaded") {
    NavigationStack {
        SymbolDetailView(
            viewModel: SymbolDetailViewModel(
                preloadedDetail: SymbolDetail.mockOm,
                service: MockRecognitionService.preview,
                favouritesRepo: UserDefaultsFavouritesRepository()
            )
        )
    }
    .preferredColorScheme(.dark)
}
