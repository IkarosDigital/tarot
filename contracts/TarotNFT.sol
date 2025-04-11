// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract TarotNFT is ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    // Mapping from token ID to card metadata
    mapping(uint256 => TarotCard) public cards;

    struct TarotCard {
        string cardName;
        string suit;      // Major Arcana, Cups, Pentacles, Swords, or Wands
        bool isReversed;  // Whether the card was drawn reversed
        string mbtiType;  // Associated MBTI type
        uint256 timestamp;
    }

    constructor() ERC721("MBTI Tarot", "TAROT") {}

    function mintTarotCard(
        address recipient,
        string memory tokenURI,
        string memory cardName,
        string memory suit,
        bool isReversed,
        string memory mbtiType
    ) public onlyOwner returns (uint256) {
        _tokenIds.increment();
        uint256 newTokenId = _tokenIds.current();

        cards[newTokenId] = TarotCard(
            cardName,
            suit,
            isReversed,
            mbtiType,
            block.timestamp
        );

        _mint(recipient, newTokenId);
        _setTokenURI(newTokenId, tokenURI);

        return newTokenId;
    }

    function getCardDetails(uint256 tokenId) public view returns (TarotCard memory) {
        require(_exists(tokenId), "Card does not exist");
        return cards[tokenId];
    }
}
