(function() {
    document.addEventListener('DOMContentLoaded', function() {
        const form = document.querySelector('.form-container form');
        if (!form) return;

        const isEdit = form.getAttribute('data-is-edit') === 'true';
        const codeId = form.getAttribute('data-code-id');
        const typeId = form.getAttribute('data-type-id');
        const conditionId = form.getAttribute('data-condition-id');
        const valueId = form.getAttribute('data-value-id');
        const backUrl = form.getAttribute('data-back-url');

        // Dropdown Toggle Logic
        window.toggleFilterDropdown = function(id) {
            const menu = document.querySelector(`#${id} .filter-dropdown-menu`);
            
            // Close others
            document.querySelectorAll('.filter-dropdown-menu').forEach(m => {
                if (m !== menu) m.classList.remove('show');
            });

            menu.classList.toggle('show');
        };

        // Select Logic
        window.selectFilterItem = function(item, wrapperId) {
            const value = item.getAttribute('data-value');
            const label = item.textContent.replace('✓', '').trim();
            const wrapper = document.getElementById(wrapperId);
            const realSelect = document.getElementById(typeId);
            const unitSpan = document.getElementById('discountUnit');

            // Update UI
            wrapper.querySelector('.filter-value').textContent = label;
            wrapper.querySelectorAll('.filter-item').forEach(el => el.classList.remove('selected'));
            item.classList.add('selected');
            wrapper.querySelector('.filter-dropdown-menu').classList.remove('show');

            // Update Hidden Select
            realSelect.value = value;
            
            // Update Unit and position
            if (unitSpan) {
                unitSpan.textContent = value === 'percent' ? '%' : 'đ';
                const input = document.getElementById(valueId);
                if (input) updateUnitPosition(input, unitSpan);
            }
        };

        // --- Number Formatting Logic ---
        function formatVN(val) {
            if (!val) return "";
            let num = val.toString().replace(/\D/g, "");
            if (num === "") return "";
            return Number(num).toLocaleString('vi-VN').replace(/,/g, '.');
        }

        function unformatVN(val) {
            return val.toString().replace(/\./g, "");
        }

        const conditionInput = document.getElementById(conditionId);
        const valueInput = document.getElementById(valueId);
        const realSelect = document.getElementById(typeId);

        function handleFormat(input, isValueField = false) {
            input.addEventListener('blur', function() {
                if (isValueField && realSelect.value !== 'fixed') return;
                this.value = formatVN(this.value);
                const unit = isValueField ? document.getElementById('discountUnit') : this.parentElement.querySelector('.value-unit');
                updateUnitPosition(this, unit);
            });

            input.addEventListener('focus', function() {
                this.value = unformatVN(this.value);
                const unit = isValueField ? document.getElementById('discountUnit') : this.parentElement.querySelector('.value-unit');
                updateUnitPosition(this, unit);
            });
        }

        if (conditionInput) handleFormat(conditionInput);
        if (valueInput) handleFormat(valueInput, true);

        // Strip dots before submit
        form.addEventListener('submit', function() {
            if (conditionInput) conditionInput.value = unformatVN(conditionInput.value);
            if (valueInput && realSelect.value === 'fixed') {
                valueInput.value = unformatVN(valueInput.value);
            }
        });

        // Dynamic Unit Positioning Logic
        const widthMeasure = document.getElementById('widthMeasure');
        function updateUnitPosition(input, unitSpan) {
            if (!input || !unitSpan || !widthMeasure) return;
            
            // Copy text and font styles to measurement span
            widthMeasure.textContent = input.value || "0";
            const style = window.getComputedStyle(input);
            widthMeasure.style.font = style.font;
            widthMeasure.style.letterSpacing = style.letterSpacing;

            const textWidth = widthMeasure.offsetWidth;
            const inputPaddingLeft = parseInt(style.paddingLeft);
            
            // Set unit position immediately after text
            unitSpan.style.left = (inputPaddingLeft + textWidth + 8) + 'px';
        }

        // Bind events for dynamic positioning
        const inputsToTrack = [
            { id: conditionId, unitClass: 'value-unit' },
            { id: valueId, unitId: 'discountUnit' }
        ];

        inputsToTrack.forEach(cfg => {
            if (!cfg.id) return;
            const input = document.getElementById(cfg.id);
            const unit = cfg.unitId ? document.getElementById(cfg.unitId) : input?.parentElement.querySelector(`.${cfg.unitClass}`);
            
            if (input && unit) {
                const update = () => updateUnitPosition(input, unit);
                input.addEventListener('input', update);
                // Also update on format/unformat
                input.addEventListener('blur', update);
                input.addEventListener('focus', update);

                // Initial position
                setTimeout(update, 100);
            }
        });
        // --- End Number Formatting ---
        
        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.filter-dropdown-wrapper')) {
                document.querySelectorAll('.filter-dropdown-menu').forEach(m => m.classList.remove('show'));
            }
        });

        // Auto-generate code
        const codeInput = document.getElementById(codeId);
        if (!isEdit && codeInput && !codeInput.value) {
            const generateCode = () => {
                const prefix = "DHK";
                const random = Math.random().toString(36).substring(2, 5).toUpperCase();
                const date = new Date().toISOString().slice(2, 10).replace(/-/g, '');
                return `${prefix}${random}${date}`;
            };
            codeInput.value = generateCode();
        }

        // Logic "Kích hoạt ngay" -> Set start date to today
        const isActiveCheckbox = form.querySelector('input[name="is_active"]');
        const startDateInput = form.querySelector('input[name="start_date"]');
        if (isActiveCheckbox && startDateInput) {
            isActiveCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    const now = new Date();
                    const year = now.getFullYear();
                    const month = String(now.getMonth() + 1).padStart(2, '0');
                    const day = String(now.getDate()).padStart(2, '0');
                    const today = `${year}-${month}-${day}`;
                    startDateInput.value = today;
                }
            });
        }

        // Back button
        const btnBack = document.getElementById('btnBack');
        if (btnBack && backUrl) {
            btnBack.addEventListener('click', function() {
                window.location.href = backUrl;
            });
        }
    });
})();
