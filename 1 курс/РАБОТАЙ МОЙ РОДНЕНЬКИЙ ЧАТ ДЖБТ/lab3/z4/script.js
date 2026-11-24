document.addEventListener('DOMContentLoaded', function() {
    
    // Get all interactive elements by their IDs
    const convertBtn = document.getElementById('convert-btn');
    const valueInputEl = document.getElementById('value-input');
    const fromUnitEl = document.getElementById('from-unit');
    const toUnitEl = document.getElementById('to-unit');
    const errorContainerEl = document.getElementById('error-container');
    const errorMessageEl = document.getElementById('error-message');
    const resultOutputEl = document.getElementById('result-output');
    const resultContainerEl = document.getElementById('result-container');

    convertBtn.addEventListener('click', function() {
        
        // 1. Clear previous errors and warnings
        errorContainerEl.hidden = true;
        errorMessageEl.textContent = '';
        resultOutputEl.textContent = '-';
        
        // Remove existing warning note if it exists
        const existingWarning = document.getElementById('warning-message');
        if (existingWarning) {
            existingWarning.remove();
        }

        // 2. Read values
        const inputValue = valueInputEl.value.trim();
        const numValue = parseFloat(inputValue);
        const fromUnit = fromUnitEl.value;
        const toUnit = toUnitEl.value;
        
        // Read the calculation system (1000 or 1024)
        const checkedRadio = document.querySelector('input[name="base-toggle"]:checked');
        const baseMultiplier = checkedRadio ? parseInt(checkedRadio.value) : 1024;

        // 3. Validation and Protection
        if (inputValue === '' || isNaN(numValue)) {
            showError('Please enter a valid numeric value.');
            return;
        }
        
        if (numValue < 0) {
            showError('Value cannot be negative.');
            return;
        }
        
        if (!fromUnit || !toUnit) {
            showError('Please select both source and target units.');
            return;
        }

        // Protection: Prevent conversion if units are identical
        if (fromUnit === toUnit) {
            showError('Source and target units cannot be identical. Please select different units.');
            return;
        }

        // Unit map: tracks if it uses bytes and its power exponent
        const unitDict = {
            'bit':  { isByte: false, exp: 0 },
            'byte': { isByte: true,  exp: 0 },
            'kb':   { isByte: true,  exp: 1 },
            'mb':   { isByte: true,  exp: 2 },
            'gb':   { isByte: true,  exp: 3 },
            'tb':   { isByte: true,  exp: 4 }
        };

        const sourceConfig = unitDict[fromUnit];
        const targetConfig = unitDict[toUnit];

        if (!sourceConfig || !targetConfig) {
            showError('System error: Invalid unit selected.');
            return;
        }

        // 4. Conversion Logic
        let totalBits = numValue;
        if (sourceConfig.isByte) {
            totalBits = numValue * 8 * Math.pow(baseMultiplier, sourceConfig.exp);
        }

        let finalResult = totalBits;
        if (targetConfig.isByte) {
            finalResult = totalBits / (8 * Math.pow(baseMultiplier, targetConfig.exp));
        }

        // 5. Output Formatting & Safe Limits Protection
        let formattedResult;
        let showWarning = false;

        // Protection: Check if value exceeds safe integer limits
        if (finalResult > Number.MAX_SAFE_INTEGER || numValue > Number.MAX_SAFE_INTEGER) {
            formattedResult = finalResult.toExponential(4);
            showWarning = true;
        } else {
            // Round to 4 decimal places to avoid garbage zeroes (e.g. 0.10000000000000001 -> 0.1)
            let roundedResult = parseFloat(finalResult.toFixed(4));
            
            // If the value is so small that toFixed(4) makes it 0, but it is actually > 0,
            // fall back to exponential notation to avoid losing the data completely.
            if (roundedResult === 0 && finalResult > 0) {
                formattedResult = finalResult.toExponential(4);
            } else {
                formattedResult = roundedResult.toString();
            }
        }

        // 6. Output the result
        resultOutputEl.textContent = formattedResult;

        // Inject warning footnote dynamically if needed
        if (showWarning) {
            const warningEl = document.createElement('p');
            warningEl.id = 'warning-message';
            // Styling the warning right in JS to avoid altering the CSS file again
            warningEl.style.color = '#fbbf24'; 
            warningEl.style.fontSize = '0.85rem';
            warningEl.style.marginTop = '0.75rem';
            warningEl.textContent = '* Note: The value exceeds the JavaScript safe integer limit. Precision loss may occur.';
            
            resultContainerEl.appendChild(warningEl);
        }
    });

    // Helper function to display errors
    function showError(msg) {
        errorMessageEl.textContent = msg;
        errorContainerEl.hidden = false;
    }
});