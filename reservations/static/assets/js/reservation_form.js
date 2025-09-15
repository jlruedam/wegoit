document.addEventListener("DOMContentLoaded", () => {
    const paxInput = document.getElementById("id_pax");
    const basePriceInput = document.getElementById("id_base_price");
    const netPaymentInput = document.getElementById("id_net_payment");

    function updateNetPayment() {
        const pax = parseInt(paxInput.value) || 0;
        const basePrice = parseFloat(basePriceInput.value) || 0;
        const total = pax * basePrice;
        netPaymentInput.value = total.toFixed(2);
    }

    paxInput.addEventListener("input", updateNetPayment);
});