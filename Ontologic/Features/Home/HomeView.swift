// MARK: - HomeView.swift

import SwiftUI

struct HomeView: View {

    @StateObject private var viewModel = HomeViewModel()

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 28) {

                // MARK: Hero
                heroSection

                // MARK: Recent
                if !viewModel.recentEntries.isEmpty {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Recent Recognitions")
                            .ontoSectionHeader()
                            .padding(.horizontal, 20)

                        ScrollView(.horizontal, showsIndicators: false) {
                            HStack(spacing: 12) {
                                ForEach(viewModel.recentEntries) { entry in
                                    recentCard(entry)
                                }
                            }
                            .padding(.horizontal, 20)
                        }
                    }
                }

                // MARK: Featured
                if let symbol = viewModel.featuredSymbol {
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Symbol of the Day")
                            .ontoSectionHeader()
                            .padding(.horizontal, 20)

                        featuredCard(symbol)
                            .padding(.horizontal, 20)
                    }
                }
            }
            .padding(.bottom, 32)
        }
        .background(Color.ontoBackground_fallback().ignoresSafeArea())
        .navigationTitle("Ontologic")
        .navigationBarTitleDisplayMode(.large)
    }

    // MARK: Hero section

    private var heroSection: some View {
        VStack(spacing: 16) {
            ZStack {
                Circle()
                    .fill(
                        RadialGradient(
                            colors: [.ontoPrimary_fallback().opacity(0.3), .clear],
                            center: .center,
                            startRadius: 20,
                            endRadius: 100
                        )
                    )
                    .frame(width: 200, height: 200)

                Image(systemName: "scribble.variable")
                    .font(.system(size: 64, weight: .thin))
                    .foregroundStyle(
                        LinearGradient(
                            colors: [.ontoPrimary_fallback(), .ontoSecondary_fallback()],
                            startPoint: .topLeading,
                            endPoint: .bottomTrailing
                        )
                    )
            }

            VStack(spacing: 6) {
                Text("Decode Any Symbol")
                    .ontoPrimaryTitle()

                Text("Draw a symbol and discover its meaning, origin and significance.")
                    .font(.ontoBodyMedium)
                    .foregroundColor(.ontoTextSecondary_fallback())
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 32)
            }
        }
        .frame(maxWidth: .infinity)
        .padding(.top, 24)
    }

    // MARK: Recent card

    private func recentCard(_ entry: HistoryEntry) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            ZStack {
                RoundedRectangle(cornerRadius: 10, style: .continuous)
                    .fill(Color.ontoPrimary_fallback().opacity(0.12))
                    .frame(height: 60)
                Image(systemName: entry.topCandidate.category.iconName)
                    .font(.system(size: 28))
                    .foregroundColor(.ontoPrimary_fallback())
            }

            Text(entry.topCandidate.name)
                .font(.ontoLabelLarge)
                .foregroundColor(.ontoTextPrimary_fallback())
                .lineLimit(1)

            Text(entry.date, style: .relative)
                .font(.ontoLabelSmall)
                .foregroundColor(.ontoTextTertiary_fallback())
        }
        .frame(width: 110)
        .padding(12)
        .ontoCard(cornerRadius: 14)
    }

    // MARK: Featured card

    private func featuredCard(_ symbol: SymbolDetail) -> some View {
        NavigationLink(value: SymbolCandidate(
            name: symbol.name,
            category: symbol.category,
            confidence: 1.0
        )) {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(Color.ontoPrimary_fallback().opacity(0.15))
                        .frame(width: 60, height: 60)
                    Image(systemName: symbol.category.iconName)
                        .font(.system(size: 26))
                        .foregroundColor(.ontoPrimary_fallback())
                }

                VStack(alignment: .leading, spacing: 4) {
                    Text(symbol.name)
                        .font(.ontoHeadlineMedium)
                        .foregroundColor(.ontoTextPrimary_fallback())

                    Text(symbol.summary)
                        .font(.ontoBodySmall)
                        .foregroundColor(.ontoTextSecondary_fallback())
                        .lineLimit(2)
                }

                Spacer()

                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.ontoTextTertiary_fallback())
            }
            .padding(16)
            .ontoCard()
        }
        .buttonStyle(.plain)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        HomeView()
    }
    .preferredColorScheme(.dark)
}
