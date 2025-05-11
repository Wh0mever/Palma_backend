import { FormFieldsProps } from "@/typing/interfaces.ts";
import NewAddDialog from "@/components/others/NewAddDialog.tsx";
import ClientsFormFields from "@/components/forms/ClientsFormFields.tsx";
import useAxiosPost from "@/hooks/useAxiosPost.ts";
import { z } from "zod";
import TextareaFormField from "@/components/others/TextareaFormField.tsx";
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx";
import { api } from "@/services/api.ts";
import clsx from "clsx";

const OrdersFormFields = ({ form }: FormFieldsProps) => {
  const { data: clientsData, isLoading: clientsLoading } =
    api.useGetClientsQuery("");
  const { data: departmentsData, isLoading: departmentsLoading } =
    api.useGetDepartmentsQuery("");
  const { data: salesmanData, isLoading: salesmanLoading } =
    api.useGetSalesmanListQuery("");
  const {
    success: clientsSuccess,
    form: clientsForm,
    onSubmit: clientsSubmit,
    pending,
    error
  } = useAxiosPost(
    {
      full_name: z.string({
        required_error: "Пожалуйста, введите имя клиента",
      }),
      phone_number: z.string().optional(),
      comment: z.string().optional(),
      discount_percent: z.string().optional().default("0.00")
    },
    {},
    "api/clients/",
    ["Clients"]
  );

  console.log(error);
  return (
    <>
      <div
        className={clsx(
          "flex items-stretch gap-2",
        )}
      >
        <ReactSelectFormField
          idData={clientsData}
          control={form.control}
          name="client"
          label="Клиент"
          placeholder="Выберите клиента"
          isLoading={clientsLoading}
          isClient
        />

        {!clientsSuccess ? (
          <NewAddDialog
            pending={pending}
            form={clientsForm}
            submit={clientsSubmit}
            success={clientsSuccess}
            successDesc="Новый клиент успешно добавлен"
            btnText="Добавить нового клиента"
            dialogTitle="Добавить нового клиента"
            dialogDesc="Заполните все поля чтобы добавить нового клиента"
          >
            <ClientsFormFields form={clientsForm} />
          </NewAddDialog>
        ) : null}
      </div>
      <ReactSelectFormField
        idData={departmentsData}
        isLoading={departmentsLoading}
        control={form.control}
        name="department"
        label="Отдел"
        placeholder="Выберите отдел"
      />
      <ReactSelectFormField
        idData={salesmanData}
        isLoading={salesmanLoading}
        control={form.control}
        name="salesman"
        label="Продавец"
        placeholder="Выберите продавца"
      />
      <TextareaFormField
        control={form.control}
        name="comment"
        label="Комментарий"
      />
    </>
  );
};

export default OrdersFormFields;
