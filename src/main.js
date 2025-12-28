import './style.css'

// Configuration for all supported countries
const COUNTRY_CONFIGS = {
  gb: {
    name: 'United Kingdom',
    currency: 'GBP',
    locale: 'en-GB',
    terms: {
      incomeLabel: 'Annual Income',
      expensesLabel: 'Business Expenses',
      taxName: 'Income Tax',
      insuranceName: 'National Insurance',
      takeHomeLabel: 'Take-Home Pay',
      netLabel: 'Monthly Salary (PAYE)'
    },
    taxRules: {
      personalAllowance: 12570,
      brackets: [
        { limit: 50270, rate: 0.20, name: 'Basic Rate' },
        { limit: 125140, rate: 0.40, name: 'Higher Rate' },
        { limit: Infinity, rate: 0.45, name: 'Additional Rate' }
      ],
      niThreshold: 12570,
      niUpperThreshold: 50270,
      niLowerRate: 0.06,
      niUpperRate: 0.02
    }
  },
  us: {
    name: 'United States',
    currency: 'USD',
    locale: 'en-US',
    terms: {
      incomeLabel: 'Gross Annual Income',
      expensesLabel: 'Business Deductions',
      taxName: 'Federal Income Tax',
      insuranceName: 'FICA (Self-Employment)',
      takeHomeLabel: 'Estimated Paycheck',
      netLabel: 'Monthly Paycheck'
    },
    taxRules: {
      standardDeduction: 15000, // Approx for 2025 Single
      brackets: [
        { limit: 11925, rate: 0.10 },
        { limit: 48475, rate: 0.12 },
        { limit: 103350, rate: 0.22 },
        { limit: 197300, rate: 0.24 },
        { limit: 250525, rate: 0.32 },
        { limit: 626350, rate: 0.35 },
        { limit: Infinity, rate: 0.37 }
      ],
      ficaRate: 0.153,
      ficaTaxableBase: 0.9235
    }
  },
  au: {
    name: 'Australia',
    currency: 'AUD',
    locale: 'en-AU',
    terms: {
      incomeLabel: 'Annual Income',
      expensesLabel: 'Work Related Deductions',
      taxName: 'Income Tax',
      insuranceName: 'Medicare Levy',
      takeHomeLabel: 'Take-Home Pay',
      netLabel: 'Fortnightly Pay'
    },
    taxRules: {
      thresholds: [
        { limit: 18200, rate: 0 },
        { limit: 45000, rate: 0.16 },
        { limit: 135000, rate: 0.30 },
        { limit: 190000, rate: 0.37 },
        { limit: Infinity, rate: 0.45 }
      ],
      medicareRate: 0.02
    }
  },
  ca: {
    name: 'Canada (Ontario)',
    currency: 'CAD',
    locale: 'en-CA',
    terms: {
      incomeLabel: 'Annual Income',
      expensesLabel: 'Business Expenses',
      taxName: 'Federal & Provincial Tax',
      insuranceName: 'CPP Contributions',
      takeHomeLabel: 'Take-Home Pay',
      netLabel: 'Monthly Salary'
    },
    taxRules: {
      fedBrackets: [
        { limit: 57375, rate: 0.145 },
        { limit: 114750, rate: 0.205 },
        { limit: 177882, rate: 0.26 },
        { limit: 253414, rate: 0.29 },
        { limit: Infinity, rate: 0.33 }
      ],
      provBrackets: [
        { limit: 52886, rate: 0.0505 },
        { limit: 105775, rate: 0.0915 },
        { limit: 150000, rate: 0.1116 },
        { limit: 220000, rate: 0.1216 },
        { limit: Infinity, rate: 0.1316 }
      ],
      cppRate: 0.119,
      cppLimit: 67800
    }
  }
}

let currentCountry = 'gb'

// Format currency
function formatCurrency(amount, country = currentCountry) {
  const config = COUNTRY_CONFIGS[country]
  return new Intl.NumberFormat(config.locale, {
    style: 'currency',
    currency: config.currency
  }).format(amount)
}

function calculateTax() {
  const income = parseFloat(document.getElementById('income').value) || 0
  const expenses = parseFloat(document.getElementById('expenses').value) || 0
  const profit = Math.max(0, income - expenses)
  const config = COUNTRY_CONFIGS[currentCountry]

  let incomeTax = 0
  let insurance = 0
  let details = []

  if (currentCountry === 'gb') {
    // UK Logic
    const pa = config.taxRules.personalAllowance
    if (profit > pa) {
      let remaining = profit - pa
      let prevLimit = pa
      for (const b of config.taxRules.brackets) {
        const taxableInBand = Math.min(remaining, b.limit - prevLimit)
        if (taxableInBand > 0) {
          const bandTax = taxableInBand * b.rate
          incomeTax += bandTax
          details.push(`${b.name}: ${formatCurrency(bandTax)}`)
          remaining -= taxableInBand
          prevLimit = b.limit
        }
      }
    }
    // NI Class 4
    if (profit > config.taxRules.niThreshold) {
      const lowerBandProfit = Math.min(profit, config.taxRules.niUpperThreshold) - config.taxRules.niThreshold
      insurance += lowerBandProfit * config.taxRules.niLowerRate
      if (profit > config.taxRules.niUpperThreshold) {
        insurance += (profit - config.taxRules.niUpperThreshold) * config.taxRules.niUpperRate
      }
    }
  }
  else if (currentCountry === 'us') {
    // US Federal Logic
    // SE Tax
    const seTaxable = profit * config.taxRules.ficaTaxableBase
    insurance = seTaxable * config.taxRules.ficaRate
    // SE Deduction
    const taxableProfit = Math.max(0, profit - (insurance / 2) - config.taxRules.standardDeduction)
    let remaining = taxableProfit
    let prevLimit = 0
    for (const b of config.taxRules.brackets) {
      const bandWidth = b.limit - prevLimit
      const taxableInBand = Math.min(remaining, bandWidth)
      if (taxableInBand > 0) {
        incomeTax += taxableInBand * b.rate
        remaining -= taxableInBand
        prevLimit = b.limit
      }
    }
  }
  else if (currentCountry === 'au') {
    // AU Logic
    let remaining = profit
    let prevLimit = 0
    for (const b of config.taxRules.thresholds) {
      const bandWidth = b.limit - prevLimit
      const taxableInBand = Math.min(remaining, bandWidth)
      if (taxableInBand > 0) {
        incomeTax += taxableInBand * b.rate
        remaining -= taxableInBand
        prevLimit = b.limit
      }
    }
    insurance = profit * config.taxRules.medicareRate
  }
  else if (currentCountry === 'ca') {
    // CA Logic
    // CPP
    insurance = Math.min(profit, config.taxRules.cppLimit) * config.taxRules.cppRate
    // Federal
    let remainingFed = profit
    let prevLimitFed = 0
    for (const b of config.taxRules.fedBrackets) {
      const taxable = Math.min(remainingFed, b.limit - prevLimitFed)
      if (taxable > 0) {
        incomeTax += taxable * b.rate
        remainingFed -= taxable
        prevLimitFed = b.limit
      }
    }
    // Provincial (Ontario)
    let remainingProv = profit
    let prevLimitProv = 0
    for (const b of config.taxRules.provBrackets) {
      const taxable = Math.min(remainingProv, b.limit - prevLimitProv)
      if (taxable > 0) {
        incomeTax += taxable * b.rate
        remainingProv -= taxable
        prevLimitProv = b.limit
      }
    }
  }

  const totalTax = incomeTax + insurance
  const takeHome = profit - totalTax
  const divisor = currentCountry === 'au' ? 26 : 12

  document.getElementById('taxableProfit').textContent = formatCurrency(profit)
  document.getElementById('incomeTax').textContent = formatCurrency(incomeTax)
  document.getElementById('nationalInsurance').textContent = formatCurrency(insurance)
  document.getElementById('totalTax').textContent = formatCurrency(totalTax)
  document.getElementById('takeHome').textContent = formatCurrency(takeHome)
  document.getElementById('periodicPay').textContent = formatCurrency(takeHome / divisor)

  // Update terminology
  const terms = config.terms
  document.querySelector('label[for="income"]').textContent = terms.incomeLabel + ` (${config.currency})`
  document.querySelector('label[for="expenses"]').textContent = terms.expensesLabel + ` (${config.currency})`
  document.getElementById('taxNameLabel').textContent = terms.taxName
  document.getElementById('insuranceNameLabel').textContent = terms.insuranceName
  document.getElementById('periodicLabel').textContent = terms.netLabel
}

function init() {
  const container = document.getElementById('countrySelector')
  Object.keys(COUNTRY_CONFIGS).forEach(key => {
    const btn = document.createElement('button')
    btn.className = `px-4 py-2 rounded-lg transition-all ${key === currentCountry ? 'bg-primary-500 text-white' : 'bg-white/5 hover:bg-white/10'}`
    btn.textContent = COUNTRY_CONFIGS[key].name
    btn.onclick = () => {
      currentCountry = key
      document.querySelectorAll('#countrySelector button').forEach(b => b.classList.remove('bg-primary-500', 'text-white'))
      document.querySelectorAll('#countrySelector button').forEach(b => b.classList.add('bg-white/5'))
      btn.classList.add('bg-primary-500', 'text-white')
      btn.classList.remove('bg-white/5')
      calculateTax()
    }
    container.appendChild(btn)
  })

  document.getElementById('income').oninput = calculateTax
  document.getElementById('expenses').oninput = calculateTax
  calculateTax()
}

document.addEventListener('DOMContentLoaded', init)
