// Logic gộp ngày sinh cho 3 ô chọn
document.addEventListener('DOMContentLoaded', function() {
    const daySel = document.getElementById('bday_day');
    const monthSel = document.getElementById('bday_month');
    const yearSel = document.getElementById('bday_year');
    const hiddenInput = document.getElementById('id_birthday');

    function getDaysInMonth(month, year) {
        return new Date(year, month, 0).getDate();
    }

    function updateDays() {
        if (!daySel || !monthSel || !yearSel) return;
        
        const selectedDay = parseInt(daySel.value);
        const month = parseInt(monthSel.value);
        const year = parseInt(yearSel.value);
        const daysInMonth = getDaysInMonth(month, year);

        // Xóa bớt hoặc thêm ngày vào select
        const currentDays = daySel.options.length;
        if (currentDays < daysInMonth) {
            for (let i = currentDays + 1; i <= daysInMonth; i++) {
                const opt = document.createElement('option');
                opt.value = i;
                opt.textContent = i.toString().padStart(2, '0');
                daySel.appendChild(opt);
            }
        } else if (currentDays > daysInMonth) {
            for (let i = currentDays; i > daysInMonth; i--) {
                daySel.remove(i - 1);
            }
        }

        // Nếu ngày cũ lớn hơn số ngày mới của tháng, chọn ngày cuối cùng của tháng đó
        if (selectedDay > daysInMonth) {
            daySel.value = daysInMonth;
        } else {
            daySel.value = selectedDay;
        }
        
        updateBirthday();
    }

    function updateBirthday() {
        if (!daySel || !monthSel || !yearSel || !hiddenInput) return;
        const day = daySel.value.padStart(2, '0');
        const month = monthSel.value.padStart(2, '0');
        const year = yearSel.value;
        hiddenInput.value = `${year}-${month}-${day}`;
    }

    if (daySel && monthSel && yearSel) {
        // Lần đầu chạy để khớp số ngày
        updateDays();

        daySel.addEventListener('change', updateBirthday);
        monthSel.addEventListener('change', updateDays); // Thay đổi tháng/năm thì cập nhật lại số ngày
        yearSel.addEventListener('change', updateDays);
    }
});
