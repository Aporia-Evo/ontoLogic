// MARK: - HistoryView.swift

import SwiftUI

struct HistoryView: View {

    @StateObject var viewModel: HistoryViewModel
    @State private var showClearConfirm = false

    var body: some View {
        ZStack {
            Color.ontoBackground_fallback().ignoresSafeArea()

            if viewModel.entries.isEmpty {
                EmptyStateView(
                    icon: "clock.arrow.circlepath",
                    title: "No History Yet",
                    message: "Recognised symbols will appear here."
                )
            } else {
                List {
                    ForEach(viewModel.entries) { entry in
                        NavigationLink(value: entry) {
                            HistoryRowView(entry: entry)
                        }
                        .listRowBackground(Color.ontoSurface_fallback())
                        .listRowSeparatorTint(Color.ontoSurfaceSecond_fallback())
                    }
                    .onDelete { offsets in
                        viewModel.delete(at: offsets)
                    }
                }
                .listStyle(.plain)
                .scrollContentBackground(.hidden)
            }
        }
        .navigationTitle("History")
        .navigationBarTitleDisplayMode(.large)
        .toolbar {
            if !viewModel.entries.isEmpty {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Clear All") { showClearConfirm = true }
                        .foregroundColor(.ontoDestructive_fallback())
                }
            }
        }
        .confirmationDialog(
            "Clear all history?",
            isPresented: $showClearConfirm,
            titleVisibility: .visible
        ) {
            Button("Clear All", role: .destructive) { viewModel.clearAll() }
            Button("Cancel", role: .cancel) {}
        }
        .onAppear { viewModel.reload() }
    }
}

// MARK: - HistoryRowView

struct HistoryRowView: View {
    let entry: HistoryEntry

    var body: some View {
        HStack(spacing: 14) {
            ZStack {
                Circle()
                    .fill(Color.ontoPrimary_fallback().opacity(0.15))
                    .frame(width: 42, height: 42)
                Image(systemName: entry.topCandidate.category.iconName)
                    .font(.system(size: 18))
                    .foregroundColor(.ontoPrimary_fallback())
            }

            VStack(alignment: .leading, spacing: 4) {
                Text(entry.topCandidate.name)
                    .font(.ontoHeadlineSmall)
                    .foregroundColor(.ontoTextPrimary_fallback())

                HStack(spacing: 6) {
                    CategoryBadge(category: entry.topCandidate.category)
                    ConfidenceBadge(score: entry.topCandidate.confidence)
                }
            }

            Spacer()

            Text(entry.date, style: .relative)
                .font(.ontoLabelSmall)
                .foregroundColor(.ontoTextTertiary_fallback())
        }
        .padding(.vertical, 6)
    }
}

// MARK: - Preview

#Preview {
    NavigationStack {
        HistoryView(viewModel: HistoryViewModel.preview())
    }
    .preferredColorScheme(.dark)
}
