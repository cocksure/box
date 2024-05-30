document.addEventListener('DOMContentLoaded', function () {
    let detailCounter = 1;

    function addDetail(type) {
        let material = document.getElementById(`${type}_material`).value;
        let amount = document.getElementById(`${type}_amount`).value;
        let comment = document.getElementById(`${type}_comment`).value;

        if (!material || !amount) {
            alert('Пожалуйста, заполните все поля.');
            return;
        }

        let materialFieldName = `${type}_material_` + detailCounter;
        let amountFieldName = `${type}_amount_` + detailCounter;
        let commentFieldName = `${type}_comment_` + detailCounter;

        let existingMaterialField = document.getElementById(materialFieldName);
        let existingAmountField = document.getElementById(amountFieldName);
        let existingCommentField = document.getElementById(commentFieldName);

        if (!existingMaterialField && !existingAmountField && !existingCommentField) {
            let materialField = `<input type="hidden" name="${materialFieldName}" class="${type}_material" value="${material}">`;
            let amountField = `<input type="hidden" name="${amountFieldName}" class="${type}_amount" value="${amount}">`;
            let commentField = `<input type="hidden" name="${commentFieldName}" class="${type}_comment" value="${comment}">`;

            document.getElementById('id_form').insertAdjacentHTML('beforeend', materialField);
            document.getElementById('id_form').insertAdjacentHTML('beforeend', amountField);
            document.getElementById('id_form').insertAdjacentHTML('beforeend', commentField);

            let newRow = `<tr>
                <td>${material}</td>
                <td>${amount}</td>
                <td>${comment}</td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm delete-btn ml-2"><i class="bi bi-trash"></i></button>
                </td>
            </tr>`;

            document.getElementById(`${type}_materials_table`).insertAdjacentHTML('beforeend', newRow);

            document.querySelectorAll('.delete-btn').forEach(function (button) {
                button.addEventListener('click', function () {
                    let row = button.closest('tr');
                    row.remove();

                    let material = row.cells[0].textContent;
                    let amount = row.cells[1].textContent;
                    let comment = row.cells[2].textContent;

                    let hiddenMaterialFields = document.querySelectorAll(`input[name^="${type}_material_"]`);
                    let hiddenAmountFields = document.querySelectorAll(`input[name^="${type}_amount_"]`);
                    let hiddenCommentFields = document.querySelectorAll(`input[name^="${type}_comment_"]`);

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

            document.getElementById(`${type}_material`).value = '';
            document.getElementById(`${type}_amount`).value = '';
            document.getElementById(`${type}_comment`).value = '';

            $('#myModalCreate').modal('hide');

            detailCounter++;
        } else {
            console.log('Fields already exist for this detail');
        }
    }

    function handleSubmit(type, url) {
        document.getElementById('id_form').addEventListener('submit', function (event) {
            event.preventDefault();

            document.getElementById('detail_counter').value = detailCounter;

            let formData = new FormData(this);
            let details = document.querySelectorAll(`.${type}_material, .${type}_amount, .${type}_comment`);

            details.forEach(function (detail) {
                formData.append(detail.name, detail.value);
            });

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    } else {
                        window.location.href = '{% url "depo:' + type + '-list" %}';
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });
    }

    window.addDetail = addDetail;
    window.handleSubmit = handleSubmit;
});
