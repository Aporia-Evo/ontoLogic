// MARK: - SymbolDetailViewModel.swift

import Foundation
import Combine

enum SymbolDetailState {
    case loading
    case loaded(SymbolDetail)
    case error(RecognitionError)
}

final class SymbolDetailViewModel: ObservableObject {

    @Published private(set) var state: SymbolDetailState = .loading
    @Published var isFavourite: Bool = false

    private let service: any RecognitionServiceProtocol
    private let favouritesRepo: FavouritesRepositoryProtocol
    private let candidate: SymbolCandidate?

    // MARK: Init from candidate (loads detail lazily)
    init(
        candidate: SymbolCandidate,
        service: any RecognitionServiceProtocol,
        favouritesRepo: FavouritesRepositoryProtocol
    ) {
        self.candidate = candidate
        self.service = service
        self.favouritesRepo = favouritesRepo
        self.isFavourite = false
    }

    // MARK: Init with preloaded detail (e.g. from Favourites)
    init(
        preloadedDetail: SymbolDetail,
        service: any RecognitionServiceProtocol,
        favouritesRepo: FavouritesRepositoryProtocol
    ) {
        self.candidate = nil
        self.service = service
        self.favouritesRepo = favouritesRepo
        self.state = .loaded(preloadedDetail)
        self.isFavourite = favouritesRepo.contains(id: preloadedDetail.id)
    }

    // MARK: Intents

    @MainActor
    func loadIfNeeded() async {
        guard case .loading = state, let candidate else { return }
        do {
            let detail = try await service.fetchDetail(for: candidate)
            state = .loaded(detail)
            isFavourite = favouritesRepo.contains(id: detail.id)
        } catch let err as RecognitionError {
            state = .error(err)
        } catch {
            state = .error(.unknown(underlying: error))
        }
    }

    func toggleFavourite() {
        guard case .loaded(var detail) = state else { return }
        if isFavourite {
            favouritesRepo.remove(id: detail.id)
        } else {
            detail.isFavourite = true
            favouritesRepo.add(detail)
        }
        isFavourite.toggle()
    }
}
