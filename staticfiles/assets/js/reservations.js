$('#reservationTable').DataTable({
    responsive: {
        details: {
            type: 'column',
            target: 'tr'
        }
    },
    columnDefs: [
        { responsivePriority: 1, targets: 0 }, // Tipo Documento
        { responsivePriority: 2, targets: 1 }, // Nombre Cliente
        { responsivePriority: 3, targets: 2 }, // Documento Cliente
        { responsivePriority: 4, targets: 5 }, // Total a pagar
        { responsivePriority: 5, targets: 8 }  // Estado
        // El resto se oculta en móviles y aparece en el detalle desplegable
    ],
    autoWidth: false,
    language: {
        url: "//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json"
    }
});
