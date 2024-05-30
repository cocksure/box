function addDetail(material, amount, comment, type, counter) {
    let materialKey = type === 'incoming' ? 'incoming_material' : 'outgoing_material';
    let amountKey = type === 'incoming' ? 'incoming_amount' : 'outgoing_amount';
    let commentKey = type === 'incoming' ? 'incoming_comment' : 'outgoing_comment';

    let materialFieldName = type + '_material_' + counter;
    let amountFieldName = type + '_amount_' + counter;
    let commentFieldName = type + '_comment_' + counter;

    let incomingMaterial = document.getElementById(material).value;
    let incomingAmount = document.getElementById(amount).value;
    let incomingComment = document.getElementById(comment).value;

    if (!incomingMaterial || !incomingAmount) {
        alert('Пожалуйста, заполните все поля.');
        return;
    }

    let existingMaterialField = document.getElementById(materialFieldName);
    let existingAmountField = document.getElementById(amountFieldName);
    let existingCommentField = document.getElementById(commentFieldName);

    if (!existingMaterialField && !existingAmountField && !existingCommentField) {
        let materialField = '<input type="hidden" name="' + materialFieldName + '" class="' + type + '_material" value="' + incomingMaterial + '">';
        let amountField = '<input type="hidden" name="' + amountFieldName + '" class="' + type + '_amount" value="' + incomingAmount + '">';
        let commentField = '<input type="hidden" name="' + commentFieldName + '" class="' + type + '_comment" value="' + incomingComment + '">';

        document.getElementById('id_form').insertAdjacentHTML('beforeend', materialField);
        document.getElementById('id_form').insertAdjacentHTML('beforeend', amountField);
        document.getElementById('id_form').insertAdjacentHTML('beforeend', commentField);

        let newRow = '<tr>' +
            '<td>' + incomingMaterial + '</td>' +
            '<td>' + incomingAmount + '</td>' +
            '<td>' + incomingComment + '</td>' +
            '<td>' +
            '<button type="button" class="btn btn-danger btn-sm delete-btn ml-2"><i class="bi bi-trash"></i></button>' +
            '</td>' +
            '</tr>';

        document.getElementById(type + '_materials_table').insertAdjacentHTML('beforeend', newRow);

        document.querySelectorAll('.delete-btn').forEach(function (button) {
            button.addEventListener('click', function () {
                let row = button.closest('tr');
                row.remove();

                let material = row.cells[0].textContent;
                let amount = row.cells[1].textContent;
                let comment = row.cells[2].textContent;

                let hiddenMaterialFields = document.querySelectorAll('input[name^="' + type + '_material_"]');
                let hiddenAmountFields = document.querySelectorAll('input[name^="' + type + '_amount_"]');
                let hiddenCommentFields = document.querySelectorAll('input[name^="' + type + '_comment_"]');

                hiddenMaterialFields.forEach(function (field) {
                    if (field.value === material) {
                        field.remove();
                    }
                });

                hiddenAmountFields.forEach(function (field) {
                    if (field.value === amount) {
                        field.remove();
                    }
                });

                hiddenCommentFields.forEach(function (field) {
                    if (field.value === comment) {
                        field.remove();
                    }
                });
            });
        });

        document.getElementById(material).value = '';
        document.getElementById(amount).value = '';
        document.getElementById(comment).value = '';

        counter++;
    } else {
        console.log('Fields already exist for this detail');
    }
}
