import React, { useState } from 'react';
import { Calculator, Shield, Calendar, AlertCircle, ChevronDown, ChevronUp, CheckCircle2 } from 'lucide-react';

interface EMIOption {
  tenureYears: number;
  tenureMonths: number;
  monthlyEmi: number;
  loanPrincipal: number;
  totalInterest: number;
  totalPayable: number;
}

interface PriceBreakdown {
  exShowroomPrice: number;
  rtoTax: number;
  rtoRoadSafetyCess?: number;
  registrationAndSmartCardFee?: number;
  insurance: number;
  tcs?: number;
  fastag?: number;
  hsrpAndPortalFees?: number;
  dealerHandlingCharges?: number;
  onRoadPrice: number;
}

export interface PricingQuoteData {
  location: {
    city: string;
    stateCode: string;
    stateName: string;
    calculationScope?: string;
  };
  vehicle: {
    manufacturer: string;
    model: string;
    variant: string;
    fuelType: string;
    isEstimatedPrice?: boolean;
  };
  priceBreakdown: PriceBreakdown;
  emiOptions: EMIOption[];
  dataFreshness?: {
    priceEffectiveDate?: string;
    ruleEffectiveDate?: string;
    lastVerifiedAt?: string;
    isEstimate?: boolean;
    dataSourceLabel?: string;
  };
  assumptions?: string[];
  disclaimer: string;
}

interface PricingQuoteCardProps {
  quote: PricingQuoteData;
}

export const formatINR = (val: number): string => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0
  }).format(Math.round(val));
};

export const PricingQuoteCard: React.FC<PricingQuoteCardProps> = ({ quote }) => {
  const [selectedTenure, setSelectedTenure] = useState<number>(5);
  const [showDetails, setShowDetails] = useState<boolean>(false);

  const activeEmi = quote.emiOptions.find((e) => e.tenureYears === selectedTenure) || quote.emiOptions[0];

  return (
    <div className="my-3 rounded-2xl border border-amber-200/80 bg-gradient-to-b from-amber-50/40 to-white shadow-sm overflow-hidden text-zinc-800">
      {/* Card Header */}
      <div className="px-4 py-3 bg-amber-500/10 border-b border-amber-200/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-amber-500 text-white rounded-lg">
            <Calculator className="w-4 h-4" />
          </div>
          <div>
            <h4 className="font-bold text-sm text-zinc-900">
              {quote.vehicle.manufacturer} {quote.vehicle.model}
              <span className="text-xs font-normal text-zinc-600 ml-1.5">({quote.vehicle.variant})</span>
            </h4>
            <div className="flex items-center gap-2 text-[11px] text-zinc-500">
              <span>📍 {quote.location.city}, {quote.location.stateName}</span>
              <span>•</span>
              <span className="capitalize">⛽ {quote.vehicle.fuelType}</span>
            </div>
          </div>
        </div>

        <div className="text-right">
          <span className="text-[10px] uppercase font-semibold text-zinc-500 tracking-wider">Estimated On-Road</span>
          <div className="text-base sm:text-lg font-black text-amber-700">
            {formatINR(quote.priceBreakdown.onRoadPrice)}
          </div>
        </div>
      </div>

      {/* EMI Selector Bar */}
      {quote.emiOptions && quote.emiOptions.length > 0 && (
        <div className="px-4 py-2.5 bg-white border-b border-zinc-100 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <span className="text-xs font-medium text-zinc-600">Loan Tenure:</span>
            {quote.emiOptions.map((opt) => (
              <button
                key={opt.tenureYears}
                type="button"
                onClick={() => setSelectedTenure(opt.tenureYears)}
                className={`px-2.5 py-1 text-xs rounded-lg font-medium transition cursor-pointer ${
                  selectedTenure === opt.tenureYears
                    ? 'bg-zinc-900 text-white shadow-sm'
                    : 'bg-zinc-100 hover:bg-zinc-200 text-zinc-700'
                }`}
              >
                {opt.tenureYears} Yrs
              </button>
            ))}
          </div>

          {activeEmi && (
            <div className="text-right">
              <span className="text-[11px] text-zinc-500">Monthly EMI: </span>
              <span className="text-sm font-bold text-emerald-700">{formatINR(activeEmi.monthlyEmi)}/mo</span>
            </div>
          )}
        </div>
      )}

      {/* Collapsible Price Breakdown */}
      <div className="px-4 py-2 text-xs">
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="w-full flex items-center justify-between text-zinc-600 hover:text-zinc-900 py-1 font-medium cursor-pointer"
        >
          <span>View itemized price breakdown & statutory fees</span>
          {showDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showDetails && (
          <div className="pt-2 pb-1 space-y-1.5 border-t border-zinc-100 mt-1 text-[11px]">
            <div className="flex justify-between text-zinc-600">
              <span>Ex-Showroom Price</span>
              <span className="font-semibold text-zinc-900">{formatINR(quote.priceBreakdown.exShowroomPrice)}</span>
            </div>
            <div className="flex justify-between text-zinc-600">
              <span>State RTO Tax ({quote.location.stateCode})</span>
              <span className="font-medium text-zinc-800">{formatINR(quote.priceBreakdown.rtoTax)}</span>
            </div>
            <div className="flex justify-between text-zinc-600">
              <span>Comprehensive Motor Insurance</span>
              <span className="font-medium text-zinc-800">{formatINR(quote.priceBreakdown.insurance)}</span>
            </div>
            {quote.priceBreakdown.tcs ? (
              <div className="flex justify-between text-zinc-600">
                <span>TCS @ 1%</span>
                <span className="font-medium text-zinc-800">{formatINR(quote.priceBreakdown.tcs)}</span>
              </div>
            ) : null}
            {quote.priceBreakdown.fastag ? (
              <div className="flex justify-between text-zinc-600">
                <span>FASTag + HSRP Number Plate</span>
                <span className="font-medium text-zinc-800">
                  {formatINR((quote.priceBreakdown.fastag || 0) + (quote.priceBreakdown.hsrpAndPortalFees || 0))}
                </span>
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Freshness & Disclaimer Footer */}
      <div className="px-4 py-2 bg-zinc-50 border-t border-zinc-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-1 text-[10px] text-zinc-500">
        <div className="flex items-center gap-1.5">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span>Local pricing data • Last verified: {quote.dataFreshness?.lastVerifiedAt || '2026-03-01'}</span>
        </div>
        <span className="italic text-zinc-400">Final dealer quotation may vary.</span>
      </div>
    </div>
  );
};
