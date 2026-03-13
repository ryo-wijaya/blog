---
layout: post
title: "Equities & Derivatives Fundamentals"
description: >-
  Reference on how the equity derivatives markets work. Covers stocks, exchanges, market makers, options, futures, forwards, swaps, and the macro factors that move markets.
author: ryo
date: 2026-03-03 21:03:45 +0800
categories: [Finance]
tags: [finance, stocks, derivatives, markets]
toc: true
comments: true
pin: false
published: true
---

## Overview

Equities can refer to REITs, private equity, commodities, cryptocurrency, and some other stuff. Here I will mostly be referring to stocks and it's derivatives. Focused on US markets where I trade and invest.

---

## Stocks

A stock represents fractional ownership in a company. Owning shares gives you a piece of the company's assets and earnings.

### Basic Key Metrics

- **Market Cap** - share price times shares outstanding. The total market value of the company.
- **P/E Ratio** - price divided by earnings per share. How much investors are paying per dollar of earnings. Only really useful when compared to similar companies.
- **EPS** - net income divided by shares outstanding. Earnings on a per-share basis.
- **Dividend Yield** - annual dividend divided by share price. How much dividend income the stock generates relative to its price.
- **Beta** - volatility relative to the broader market. Beta above 1 means the stock moves more than the market on average.
- **Float** - the number of shares actually available for public trading, excluding insider-held or restricted shares. Low float stocks can be very volatile.

### Corporate Actions

These are company-level events that directly affect stocks.

- **Stock Split** - divides existing shares into more shares at a proportionally lower price. Overall market cap will stay the same.
- **Dividend** - cash or additional shares paid out to shareholders from earnings.
- **Buyback** - company repurchases its own shares. Reduces supply and typically increases EPS since the same earnings are spread across fewer shares.
- **Spin-off** - a subsidiary is separated from the parent and listed as its own company.

---

## Exchanges and Indices

An exchange is a regulated marketplace where securities are traded. An index is a benchmark that tracks market performance, some examples:

- **S&P 500** - 500 large-cap US companies.
- **NASDAQ-100 (NDX)** - top 100 non-financial NASDAQ companies. Tech heavy.
- **NASDAQ Composite** - all stocks listed on NASDAQ. Also tech heavy.
- **Dow Jones (DJIA)** - 30 large blue-chip US companies.
- **Russell 2000** - 2000 small-cap US companies. Used to track small-cap health separately from large-caps.

### Order Types

- **Market Order** - executes immediately at whatever the best available price is.
- **Limit Order** - only executes at your specified price or better. Fill is not guaranteed.
- **Stop Order** - becomes a market order when a trigger price is hit. Unlike market and limit orders these are usually hidden on the order book.

---

### Stock Market Data Classification

We make buy and sell decisions based on market data. There are 2 main tiers of data accessible for us retail investors/traders.

**Level 1** is the basic stuff that's usually free everywhere, the current best bid, ask, and last traded price, as well as volume.

**Level 2** shows the full order book depth, meaning all the bids and asks queued up at different price levels, not just the top one. You can see where large buy or sell walls are sitting, which gives a better picture of short-term supply and demand. Usually you have to pay for this service, either from your broker or an exeternal provider, but some may provide limited amounts of this data for free, for example the [Moomoo](https://www.moomoo.com) broker. 

## Market Makers

A market maker continuously quotes both a bid and ask price, and will usually be the one ready to make the trade with you. For example, when selling, you typically don't sell to a buyer, but rather you sell to a market maker that then sells to a buyer.

They profit from the **bid-ask spread**, the gap between what they buy at and sell at. In exchange for that, they take on inventory risk and have to hedge it constantly. If they buy a lot of a stock and it drops, that's a loss. So they hedge using related instruments, like options, futures, correlated stocks, whatever will keep them at net zero. Basically they do not want to take an overall long or short position on a stock.

Modern market makers do this algorithmically at super high speeds. Retail orders often get routed through market makers via **payment for order flow (PFOF)**, where brokers sell their order flow to market makers who then execute it. The broker gets paid, the market maker gets a guaranteed stream of orders to fill, and the retail trader usually gets a slightly better price than the quoted spread.

---

## Derivatives

A derivative is a contract whose value is derived from an underlying asset, like a stock, index, commodity, currency, or interest rate. It takes the underlying asset and adds an additional layer of complexity to it 🗿. The main use cases are hedging, speculation, and arbitrage (exploiting price differences across markets).

The main types are options, futures, forwards, and swaps. And for us retail investors/traders, we usually only deal with options and futures.

---

## Options

An option gives the buyer the **right, but not the obligation**, to buy or sell an asset at a set price (called the strike price) before or on an expiration date. The buyer pays a premium for this right (also called a contract). The seller collects the premium but takes on the obligation to fulfill the contract if exercised.

- **Call** - the right to buy the underlying at the strike. Profitable when price rises above strike + premium paid.
- **Put** - the right to sell the underlying at the strike. Profitable when price falls below strike minus premium paid.

Some terms worth knowing:

- **ITM (In the Money)** - the option has intrinsic value. For a call: spot price is above the strike. For a put: spot price is below the strike.
- **OTM (Out of the Money)** - no intrinsic value. The option is purely a bet on future price movement.
- **American style** - can be exercised any time before expiration. Most equity options work this way.
- **European style** - can only be exercised at expiration. Most index options work this way.

---

## Futures

A futures contract is a standardized agreement to buy or sell an asset at a set price on a future date. Unlike options, both parties are **obligated** to fulfill the contract.

Futures are exchange-traded with a central clearinghouse sitting in between, so there's no direct counterparty risk. They require posting **margin**, a deposit that's a fraction of the full value, which is what makes them highly leveraged. Positions are also **marked to market daily**, meaning gains and losses settle every day, not just at expiration.

Common futures markets include equity indices (S&P 500, NASDAQ), fixed income (US Treasuries), commodities (oil, gold, wheat), and FX.

- **Contango** - futures price is above spot price. Normal when storage or carry costs exist.
- **Backwardation** - futures price is below spot price. Happens when near-term demand is unusually high.
- **Rollover** - closing a near-expiry contract and opening the next one to maintain exposure.

---

## Forwards

A forward is basically a futures contract that isn't exchange-traded. It's a private OTC agreement between two parties on custom terms. Mostly used by corporations for FX and commodity hedging.

---

## Swaps

A swap is an OTC agreement to exchange cash flows over time. The most common type is an interest rate swap, where two parties exchange fixed and floating interest payments on a notional amount without actually exchanging the principal. Companies use this to manage their debt exposure, like converting variable rate debt into fixed rate to avoid surprises if rates rise. Credit default swaps (like in the Big Short movie) are insurance on debt, where the buyer pays a periodic premium and the seller pays out if there's a default.

---

## Global Macro Factors

These are the broad forces that move markets. 

### Interest Rates

The Fed sets the Federal Funds Rate, the short-term benchmark that everything else prices off of.

- **Rate hike** - equities fall (companies borrow a lot of money with interest), bonds fall, dollar strengthens (attracts foreign investment). Growth usually gets hit hardest because their valuations depend heavily on discounting future earnings at a higher rate.
- **Rate cut** - equities rise (borrowing is now cheaper!), bonds rise, dollar weakens. Growth stocks benefit the most.
- **QE (Quantitative Easing)** - the Fed buys assets to inject liquidity (like government bonds for example). Bullish for risk assets.
- **QT (Quantitative Tightening)** - the Fed sells assets. Drains cash out of the system. Bearish.


### Key Economic Data Releases

**CPI (Consumer Price Index)** - monthly, mid-month. Tracks consumer inflation. Core CPI (excluding volatile food and energy) is often used to gauge underlying, longer-term inflationary trends. If it comes in hotter than expected (prices rose too much), both equities and bonds tend to sell off. This is because it signifies increase in cost of living, and people are scared banks will hike interest rates. Cooler than expected (price increase slows down) usually triggers a rally due to hopes of lowered rates.

**PCE (Personal Consumption Expenditures)** - monthly, end of month. It's like CPI but broader in some ways. The Fed's preferred inflation measure, so it carries slightly more weight than CPI in terms of what the Fed actually cares about. Same general market impact though.

**Non-Farm Payrolls (NFP)** - first Friday of every month. How many jobs were added outside agriculture. Strong jobs are good for the economy but also means the Fed has more room to keep rates higher. Weak jobs makes people worry for recession.

**FOMC Rate Decision** - 8 times a year. These are the times where the Fed will actually decide whether to raise or cut rates. Funnily enough, the actual rate decision can matters less than the language or tone around it. At the time of writing this, the chairman of the Fed is Jerome Powell, and what he says in the press conference regarding market outlook can influence market movement just as much, if not more.

**GDP Growth** - quarterly, three releases per quarter (advance, second estimate, third estimate). Two consecutive negative quarters is technically a recession apparently, and will hurt equities.

**PPI (Producer Price Index)** - monthly, mid-month. Producer-level inflation. Usually market-moving than CPI on its own. It represents the costs from the seller's perspective (CPI is from the buyer's).

**Retail Sales** - monthly, mid-month. Consumer spending data. Strong spending is good for equities. Weak spending raises concerns since consumer spending drives most of US GDP.

### Earnings Season

Four times a year companies (most of them anyways) report quarterly results. Most S&P 500 companies report within a few weeks of each quarter ending, so roughly January, April, July, and October. These are the exciting moments to look out for that can cause significant changes in a company's stock price.

**EPS and Revenue vs Estimates** - earning beats *usually* lift the stock (but honestly you can never tell, depends on micro and macro economic factors, or general people craziness). But the size of the move is usually determined by how far from expectations the beat or miss was, not just whether it beat or missed.

**Guidance** - what management says about the next quarter or the full year often moves the stock more than the actual reported numbers. Cutting guidance gets punished hard even when the current quarter looked fine or even does well.

### Risk-On vs Risk-Off

At any point, markets are roughly in one of two modes.

**Risk-on** means people are buying equities, high-yield bonds, and emerging market assets. Safe havens get sold. **Risk-off** means the opposite, people are rotating out of risky stuff and into USD, JPY, CHF, Treasuries, and gold.

### Cross-Asset Relationships

**Stocks vs Bonds** - usually inversely correlated. When economy slows, investors sell stocks (expecting lower profits) and buy bonds (safer). But when the driver is inflation, they can both rallyy and sell off at the same time (e.g. rate cuts will make existing bonds more valuable as well as make borrowing cheaper for companies, causing both to rally).

**USD vs Commodities** - commodities are priced and settled in USD, so a stronger dollar tends to push commodity prices down. E.g., when USD strengthens, it takes fewer dollars to buy the same amount of wood, which both puts pressure on the price and makes wood more expensive for people outside the USA to buy (dampening global demand).
