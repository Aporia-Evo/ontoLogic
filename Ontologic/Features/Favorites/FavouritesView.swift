// MARK: - FavouritesView.swift

import SwiftUI

struct FavouritesView: View {

    @StateObject var viewModel: FavouritesViewModel

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            if viewModel.items.isEmpty {
                EmptyStateView(
                    icon: "star.slash",
                    title: "No Favourites",
                    message: "Tap the star on any symbol detail to save it here."
                )
            } else {
                List {
                    ForEach(viewModel.items) { detail in
                        NavigationLink(value: detail) {
                            FavouriteRowView(detail: detail)
                        }
                        .listRowBackground(Color.ontoSurface_fallback())
                        .listRowSeparatorTint(Color.ontoSurfaceSecond_fallback())
                    }
                    .onDelete { offsets in
                        for index in offsets {
                            viewModel.remove(viewModel.items[index])
                        }
                    }
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
            }
        }
        .navigationTitle("Favourites")
        .navigationBarTitleDisplayMode(.large)
        .onAppear { viewModel.reload() }
    }
}

// MARK: - FavouriteRowView

struct FavouriteRowView: View {
    let detail: SymbolDetail

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle()
                    .fill(Color.yellow.opacity(0.15))
                    .frame(width: 42, height: 42)
                Image(systemName: detail.category.iconName)
                    .font(.system(size: 18))
                    .foregroundColor(.yellow)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text(detail.name)
                    .font(.ontoHeadlineSmall)
                    .foregroundColor(.ontoTextPrimary_fallback())

                Text(detail.summary)
                    .font(.ontoBodySmall)
                    .foregroundColor(.ontoTextSecondary_fallback())
                    .lineLimit(1)
            }

            Spacer()

            CategoryBadge(category: detail.category)
        }
        .padding(.vertical, 6)
    }
}

// MARK: - Preview

#Preview("Favourites — Empty") {
    NavigationStack {
        FavouritesView(viewModel: FavouritesViewModel(repository: UserDefaultsFavouritesRepository()))
    }
    .preferredColorScheme(.dark)
}
