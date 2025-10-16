document.addEventListener("DOMContentLoaded", () => {
    const paxInput = document.getElementById("id_pax");
    const basePriceInput = document.getElementById("id_base_price");
    const totalToPayInput = document.getElementById("id_total_to_pay");
    const expectedAgencyPayment = document.getElementById("id_expected_agency_payment");
    const expectedCustomerPayment = document.getElementById("id_expected_customer_payment");
    const scheduleInput = document.getElementById("id_schedule");
    const availableSpots = document.getElementById("available-spots");


    function updateTotalToPay() {
        const pax = parseInt(paxInput.value) || 0;
        const basePrice = parseFloat(basePriceInput.value) || 0;

        const total = pax * basePrice;
        totalToPayInput.value = total; // siempre con 2 decimales

        expectedAgencyPayment.value = totalToPayInput.value;
        expectedCustomerPayment.value = 0;
    }

    function calculateExpectedCustomer(){
        let balance = totalToPayInput.value - expectedAgencyPayment.value;
        if(balance<0){
            expectedAgencyPayment.value = totalToPayInput.value;
            expectedCustomerPayment.value = 0;
        }else{
            expectedCustomerPayment.value = balance;
        }
    }

    function calculateExpectedAgency(){
        let balance = totalToPayInput.value - expectedCustomerPayment.value;
         if(balance<0){
            expectedCustomerPayment.value = totalToPayInput.value;
            expectedAgencyPayment.value = 0;
        }else{
            expectedAgencyPayment.value = balance;
        }
        
    }

    function updateAvailableSpots() {
        const scheduleId = scheduleInput.value;
        if (scheduleId) {
            fetch(`/schedules/${scheduleId}/available-spots/`)
                .then(response => response.json())
                .then(data => {
                    availableSpots.textContent = data.available_spots;
                });
        }
    }

    // Calcular cuando se escriba o cambie el número de personas
    paxInput.addEventListener("input", updateTotalToPay);

    //Validar la cantidad ingresada para la agencia se complementaria con la del cliente
    expectedAgencyPayment.addEventListener("input", calculateExpectedCustomer);
    expectedCustomerPayment.addEventListener("input", calculateExpectedAgency);

    scheduleInput.addEventListener("change", updateAvailableSpots);



    // Calcular también al cargar la página (por si ya hay valores iniciales)
    updateTotalToPay();
});