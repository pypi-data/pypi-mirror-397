#!/usr/bin/env python3
"""
BCC Exchange CLI - Command Line Interface for BCC Currency Rates

This module provides a command-line interface for the BCC currency exchange rates.
"""

import asyncio
import argparse
import sys
from dinero import Dinero, currencies
from .bcc import BCCBankSource, AsyncBCCBankSource
from .oxr import OXRBankSource, AsyncOXRBankSource


def print_header(backend="bcc"):
    """Print application header."""
    print("=" * 60)
    if backend == "oxr":
        print("🏦 OXR Exchange - Currency Converter")
        print("📊 Live Exchange Rates from Open Exchange Rates")
        print("� Source: https://openexchangerates.org/")
    else:
        print("� BCC Exchange - Currency Converter")
        print("📊 Live Exchange Rates from Banque Centrale du Congo")
        print("🌐 Source: https://www.bcc.cd/")
    print("=" * 60)


def print_rates_table(rates, backend="bcc"):
    """Print exchange rates in a formatted table."""
    print(f"\n📈 Current Exchange Rates ({backend.upper()})")
    print("-" * 50)
    print(f"{'Currency':<10} {'Rate':<15} {'Source':<10}")
    print("-" * 50)

    for rate in sorted(rates, key=lambda x: x.currency):
        # Format the rate with proper decimal places
        formatted_rate = f"{float(rate.amount):,.4f}"
        print(f"{rate.currency:<10} {formatted_rate:<15} {backend.upper():<10}")

    print("-" * 50)


def print_comparison_table(bcc_rates, oxr_rates):
    """Print comparison table of rates from both sources."""
    print("\n📊 Rate Comparison: BCC vs OXR")
    print("-" * 80)
    print(f"{'Currency':<10} {'BCC Rate':<15} {'OXR Rate':<15} {'Difference':<15} {'%':<10}")
    print("-" * 80)
    
    # Create dictionaries for easy lookup
    bcc_dict = {rate.currency: rate.amount for rate in bcc_rates}
    oxr_dict = {rate.currency: rate.amount for rate in oxr_rates}
    
    # Get common currencies
    common_currencies = sorted(set(bcc_dict.keys()) & set(oxr_dict.keys()))
    
    for currency in common_currencies:
        bcc_rate = float(bcc_dict[currency])
        oxr_rate = float(oxr_dict[currency])
        difference = bcc_rate - oxr_rate
        percent_diff = (difference / oxr_rate * 100) if oxr_rate != 0 else 0
        
        print(f"{currency:<10} {bcc_rate:>13,.4f} {oxr_rate:>13,.4f} {difference:>13,.4f} {percent_diff:>8.2f}%")
    
    print("-" * 80)
    print(f"Total common currencies: {len(common_currencies)}")


def convert_currency(source, amount, from_cur, to_cur):
    """Convert currency using the given source rates."""
    try:
        if from_cur == "CDF":
            # Convert from CDF
            if to_cur == "CDF":
                return amount
            else:
                to_rate = source.get_value(to_cur)
                return amount / float(to_rate.amount)
        elif to_cur == "CDF":
            # Convert to CDF
            from_rate = source.get_value(from_cur)
            return amount * float(from_rate.amount)
        else:
            # Convert between foreign currencies
            source_currency = getattr(currencies, from_cur)
            source_amount = Dinero(amount, source_currency)
            result = source.to(source_amount, to_cur)
            return result.amount
    except Exception as e:
        raise ValueError(f"Conversion failed: {e}")


def interactive_mode(source, backend="bcc"):
    """Interactive currency converter mode."""
    print(f"\n🔄 Interactive Currency Converter ({backend.upper()})")
    print("Enter 'quit' or 'exit' to stop")
    print("-" * 30)

    # Get available currencies
    rates = source.get_values()
    available_currencies = [rate.currency for rate in rates] + ["CDF"]

    print(f"Available currencies: {', '.join(sorted(available_currencies))}")
    print()

    while True:
        try:
            # Get user input
            amount_input = input("Enter amount (or 'quit'): ").strip()
            if amount_input.lower() in ["quit", "exit", "q"]:
                break

            amount = float(amount_input)
            from_cur = input("From currency: ").strip().upper()
            to_cur = input("To currency: ").strip().upper()

            if (
                from_cur not in available_currencies
                or to_cur not in available_currencies
            ):
                print("❌ Invalid currency. Please use available currencies.")
                continue

            # Perform conversion
            result_amount = convert_currency(source, amount, from_cur, to_cur)

            print(f"✅ {amount:,.2f} {from_cur} = {result_amount:,.4f} {to_cur}")
            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print()


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="BCC Exchange - Currency converter using live BCC rates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bcc_exchange --list                    # Show all available rates
  bcc_exchange 100 USD EUR               # Convert 100 USD to EUR
  bcc_exchange 1000 EUR CDF              # Convert 1000 EUR to CDF
  bcc_exchange --interactive             # Interactive mode
  bcc_exchange --async-mode 50 GBP USD   # Use async mode
  bcc_exchange --backend oxr --list      # Show OXR rates
  bcc_exchange --compare                 # Compare BCC and OXR rates
  bcc_exchange --backend oxr 100 USD EUR # Convert using OXR backend
        """,
    )

    parser.add_argument("amount", nargs="?", type=float, help="Amount to convert")
    parser.add_argument(
        "from_currency", nargs="?", help="Source currency code (e.g., USD, EUR, CDF)"
    )
    parser.add_argument(
        "to_currency", nargs="?", help="Target currency code (e.g., USD, EUR, CDF)"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available exchange rates"
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Start interactive converter mode",
    )
    parser.add_argument(
        "--async-mode",
        "-a",
        action="store_true",
        help="Use async mode for fetching rates",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Quiet mode - only show conversion result",
    )
    parser.add_argument(
        "--backend",
        "-b",
        choices=["bcc", "oxr"],
        default="bcc",
        help="Select backend source: bcc (Banque Centrale du Congo) or oxr (Open Exchange Rates)",
    )
    parser.add_argument(
        "--compare",
        "-c",
        action="store_true",
        help="Compare rates from both BCC and OXR backends",
    )

    args = parser.parse_args()

    # Show header unless in quiet mode
    if not args.quiet:
        backend = args.backend if not args.compare else "comparison"
        if not args.compare:
            print_header(args.backend)
            print(f"🔄 Loading exchange rates from {args.backend.upper()}...")
        else:
            print("=" * 60)
            print("🏦 Exchange Rate Comparison")
            print("📊 Comparing BCC and OXR rates")
            print("=" * 60)
            print("🔄 Loading exchange rates from both sources...")

    try:
        # Handle comparison mode
        if args.compare:
            if getattr(args, "async_mode", False):
                return asyncio.run(async_compare(args))
            else:
                return sync_compare(args)
        
        # Initialize source based on backend
        if getattr(args, "async_mode", False):
            return asyncio.run(async_main(args))
        else:
            return sync_main(args)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return 0
    except Exception as e:
        if args.quiet:
            print(f"Error: {e}", file=sys.stderr)
        else:
            print(f"❌ Error: {e}")
            print("Please check your internet connection and try again.")
        return 1


def sync_compare(args):
    """Synchronous comparison function."""
    try:
        bcc = BCCBankSource()
        oxr = OXRBankSource()
        
        # Fetch rates from both sources
        bcc_rates = bcc.sync(True)
        oxr_rates = oxr.sync(True)
        oxr.set_cdf_as_base()
        oxr_rates = oxr.get_values()
        
        if not args.quiet:
            print(f"✅ BCC: {len(bcc_rates)} rates | OXR: {len(oxr_rates)} rates")
        
        # Show comparison
        print_comparison_table(bcc_rates, oxr_rates)
        return 0
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Note: OXR backend requires OXR_API_KEY environment variable")
        return 1


def sync_main(args):
    """Synchronous main function."""
    # Initialize source based on backend
    if args.backend == "oxr":
        try:
            source = OXRBankSource()
            rates = source.sync(cache=True)
            source.set_cdf_as_base()
            rates = source.get_values()
        except ValueError as e:
            print(f"❌ Error: {e}")
            print("Note: OXR backend requires OXR_API_KEY environment variable")
            return 1
    else:
        source = BCCBankSource()
        rates = source.sync(cache=True)

    if not args.quiet:
        print(f"✅ Successfully loaded {len(rates)} exchange rates")

    # Handle different modes
    if args.list:
        print_rates_table(rates, args.backend)
        return 0

    if args.interactive:
        interactive_mode(source, args.backend)
        return 0

    # Direct conversion
    if args.amount and args.from_currency and args.to_currency:
        try:
            result = convert_currency(
                source, args.amount, args.from_currency.upper(), args.to_currency.upper()
            )

            if args.quiet:
                print(f"{result:.4f}")
            else:
                print(f"\n💱 Conversion Result ({args.backend.upper()}):")
                print(
                    f"{args.amount:,.2f} {args.from_currency.upper()} = {result:,.4f} {args.to_currency.upper()}"
                )

            return 0

        except Exception as e:
            if args.quiet:
                print(f"Error: {e}", file=sys.stderr)
            else:
                print(f"❌ Conversion error: {e}")
            return 1

    # No specific action - show help
    if not args.quiet:
        print(
            "\n💡 Use --help for usage information or --interactive for interactive mode"
        )

    return 0


async def async_compare(args):
    """Asynchronous comparison function."""
    try:
        bcc = AsyncBCCBankSource()
        oxr = AsyncOXRBankSource()
        
        # Fetch rates from both sources in parallel
        bcc_rates, oxr_rates = await asyncio.gather(
            bcc.sync(True),
            oxr.sync(True)
        )
        
        oxr.set_cdf_as_base()
        oxr_rates = await oxr.get_values()
        
        if not args.quiet:
            print(f"✅ BCC: {len(bcc_rates)} rates | OXR: {len(oxr_rates)} rates")
        
        # Show comparison
        print_comparison_table(bcc_rates, oxr_rates)
        return 0
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Note: OXR backend requires OXR_API_KEY environment variable")
        return 1


async def async_main(args):
    """Asynchronous main function."""
    # Initialize source based on backend
    if args.backend == "oxr":
        try:
            source = AsyncOXRBankSource()
            rates = await source.sync(cache=True)
            source.set_cdf_as_base()
            rates = await source.get_values()
        except ValueError as e:
            print(f"❌ Error: {e}")
            print("Note: OXR backend requires OXR_API_KEY environment variable")
            return 1
    else:
        source = AsyncBCCBankSource()
        rates = await source.sync(cache=True)

    if not args.quiet:
        print(f"✅ Successfully loaded {len(rates)} exchange rates")

    # Handle different modes
    if args.list:
        print_rates_table(rates, args.backend)
        return 0

    # Direct conversion (async doesn't support interactive mode for simplicity)
    if args.amount and args.from_currency and args.to_currency:
        try:
            # For async, we'll use a simpler conversion approach
            from_cur = args.from_currency.upper()
            to_cur = args.to_currency.upper()

            if from_cur == "CDF":
                if to_cur == "CDF":
                    result = args.amount
                else:
                    to_rate = await source.get_value(to_cur)
                    result = args.amount / float(to_rate.amount)
            elif to_cur == "CDF":
                from_rate = await source.get_value(from_cur)
                result = args.amount * float(from_rate.amount)
            else:
                # Cross-currency conversion
                source_currency = getattr(currencies, from_cur)
                source_amount = Dinero(args.amount, source_currency)
                converted = await source.to(source_amount, to_cur)
                result = converted.amount

            if args.quiet:
                print(f"{result:.4f}")
            else:
                print(f"\n💱 Conversion Result (Async - {args.backend.upper()}):")
                print(f"{args.amount:,.2f} {from_cur} = {result:,.4f} {to_cur}")

            return 0

        except Exception as e:
            if args.quiet:
                print(f"Error: {e}", file=sys.stderr)
            else:
                print(f"❌ Conversion error: {e}")
            return 1

    # No specific action
    if not args.quiet:
        print("\n💡 Use --help for usage information")
        print("Note: Interactive mode not available in async mode")

    return 0


if __name__ == "__main__":
    sys.exit(main())
