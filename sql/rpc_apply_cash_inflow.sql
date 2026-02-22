create or replace function apply_cash_inflow(
    p_created_by uuid,
    p_order_id bigint,
    p_total numeric,
    p_delivery numeric,
    p_transaction_date timestamptz
)
returns table (
    transaction_id bigint,
    current_balance numeric
)
language plpgsql
as $$
declare
    v_total_change numeric := 0;
    v_balance numeric;
    v_main_transaction_id bigint;
begin
    -- Main sale transaction
    if p_total > 0 then
        insert into transactions (
            type, category_id, reference_type, reference_id,
            amount, description, created_by, transaction_date
        ) values (
            'sale', 1, 'orders', p_order_id,
            p_total, 'Order #' || p_order_id,
            p_created_by, p_transaction_date
        )
        returning id into v_main_transaction_id;

        v_total_change := v_total_change + p_total;
    end if;

    -- Delivery transaction
    if p_delivery > 0 then
        insert into transactions (
            type, category_id, reference_type, reference_id,
            amount, description, created_by, transaction_date
        ) values (
            'sale', 2, 'orders', p_order_id,
            p_delivery, 'Delivery Fee for Order #' || p_order_id,
            p_created_by, p_transaction_date
        );

        v_total_change := v_total_change + p_delivery;
    end if;

    -- Update balance
    update cash
    set balance = balance + v_total_change
    where id = 1
    returning balance into v_balance;

    -- Ledger
    insert into cash_ledgers (
        cash_id, transaction_id, direction, amount, balance_after
    ) values (
        1, v_main_transaction_id, 'in', v_total_change, v_balance
    );

    transaction_id := v_main_transaction_id;
    current_balance := v_balance;
    return next;
end;
$$;