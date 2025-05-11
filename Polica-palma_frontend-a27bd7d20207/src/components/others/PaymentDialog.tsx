import { BadgeDollarSign } from "lucide-react";
import { Button } from "../ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../ui/dialog";
import AddForm from "./AddForm";
import SelectFormField from "./SelectFormField";
import { SelectItem } from "../ui/select";
import { z } from "zod";
import TextareaFormField from "@/components/others/TextareaFormField.tsx";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import NumberFormField from "@/components/others/NumberFormField.tsx";
import useNumberValue from "@/hooks/useNumberValue.ts";
import SelectItemSkeleton from "@/components/skeletons/SelectItemSkeleton.tsx";
import ReactSelectFormField from "@/components/others/ReactSelectFormField.tsx";
import { api } from "@/services/api.ts";
import { useEffect, useState } from "react";

interface PaymentDialogProps {
  dialogTitle: string;
  dialogDescription: string;
  page: string;
  item: string | number | any;
  btnText?: string;
  text?: boolean;
  isDisabled?: boolean;
  outlay_type?: string;
  invalidatesTags: string[];
}

const PaymentDialog = ({
  dialogTitle,
  dialogDescription,
  page,
  item,
  text,
  isDisabled,
  outlay_type,
  btnText,
  invalidatesTags,
}: PaymentDialogProps) => {
  const { data } = api.useGetPaymentMethodCategoriesQuery("");
  const { data: workersData, isLoading: workersLoading } =
    api.useGetWorkersQuery("");
  const { data: optionsData, isLoading: optionsLoading } =
    api.useGetPaymentCreateOptionsQuery("");
  const [postData, { isSuccess: mutationSuccess, isLoading }] =
    api.usePostDataMutation();
  const [isSuccess, setIsSuccess] = useState<boolean>(false);
  const { numberValue, handleNumberChange } = useNumberValue(isSuccess);
  const apiUrl: string = `api/payments/${page}/`;

  useEffect(() => {
    if (mutationSuccess) {
      setIsSuccess(true);

      const timeoutId = setTimeout(() => {
        setIsSuccess(false);
      }, 500);

      return () => clearTimeout(timeoutId);
    }
  }, [mutationSuccess]);

  // const {data: hasShiftData, isLoading: hasShiftIsLoading} = api.useGetShiftStatusQuery("")
  // const [createShift, {isLoading: openPending}] = api.useCreateShiftMutation<any>()

  const FormSchema = z.object(
    outlay_type === "WORKERS"
      ? {
          payment_method: z.string({
            required_error: "Пожалуйста, выберите метод оплаты",
          }),
          payment_type: z.string({
            required_error: "Пожалуйста, выберите тип оплаты",
          }),
          amount: z.string({ required_error: "Пожалуйста, введите сумму" }),
          comment: z.string({
            required_error: "Пожалуйста, введите комментарий",
          }),
          worker: z.string({
            required_error: "Пожалуйста, выберите сотрудника",
          }),
        }
      : {
          payment_method: z.string({
            required_error: "Пожалуйста, выберите метод оплаты",
          }),
          payment_type: z.string({
            required_error: "Пожалуйста, выберите тип оплаты",
          }),
          amount: z.string({ required_error: "Пожалуйста, введите сумму" }),
          comment: z.string({
            required_error: "Пожалуйста, введите комментарий",
          }),
        }
  );

  const form = useForm<z.infer<typeof FormSchema>>({
    resolver: zodResolver(FormSchema),
  });

  async function onSubmit(data: z.infer<typeof FormSchema>) {
    try {
      await postData({
        url: apiUrl,
        body:
          outlay_type === "WORKERS"
            ? {
                payment_method: Number(data.payment_method),
                payment_type: data.payment_type,
                amount: numberValue.replace(/\s/g, ""),
                comment: data.comment,
                item: item,
                worker: data.worker,
              }
            : {
                payment_method: Number(data.payment_method),
                payment_type: data.payment_type,
                amount: numberValue.replace(/\s/g, ""),
                comment: data.comment,
                item: item,
              },
        invalidatesTags: invalidatesTags,
      });
    } catch (e) {
      console.log("POST error: ", e);
    }
  }

  return (
    <>
      {!isSuccess ? (
        <Dialog>
          <DialogTrigger disabled={isDisabled}>
            {!text ? (
              <Button
                type="button"
                size="icon"
                variant="outline"
                title="Добавить платёж"
                disabled={isDisabled}
              >
                <BadgeDollarSign className="w-4 h-4" />
              </Button>
            ) : (
              <Button variant="outline">
                <BadgeDollarSign className="mr-2 w-4 h-4" />{" "}
                {btnText ? btnText : "Оплатить долг"}
              </Button>
            )}
          </DialogTrigger>

          <DialogContent>
            <DialogHeader>
              <DialogTitle>{dialogTitle}</DialogTitle>
              <DialogDescription>{dialogDescription}</DialogDescription>
            </DialogHeader>

            <AddForm
              form={form}
              onSubmit={onSubmit}
              success={isSuccess}
              successDesc="Платёж успешно добавлен"
            >
              <SelectFormField
                control={form.control}
                name="payment_method"
                placeholder="Выберите метод оплаты"
                label="Метод оплаты"
                hasntSearch
              >
                {data && Array.isArray(data) ? (
                  data.map((item) => (
                    <div key={item.id} className="mt-4 flex flex-col gap-2">
                      <p className="ml-3 text-base font-semibold">
                        {item.name}
                      </p>
                      <div className="text-sm">
                        {item.payment_methods &&
                          Array.isArray(item.payment_methods) &&
                          item.payment_methods
                            .filter((item:any) => item?.is_active ? item : null)
                            .map((item: any) => (
                              <SelectItem
                                key={item.id}
                                value={item.id.toString()}
                              >
                                {item.name}
                              </SelectItem>
                            ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <SelectItemSkeleton />
                )}
              </SelectFormField>
              <ReactSelectFormField
                isValue
                valueData={optionsData?.payment_types}
                control={form.control}
                isLoading={optionsLoading}
                name="payment_type"
                placeholder="Выберите доход или расход"
                label="Доход / расход"
              />
              {outlay_type === "WORKERS" ? (
                <ReactSelectFormField
                  idData={workersData}
                  isLoading={workersLoading}
                  control={form.control}
                  name="worker"
                  placeholder="Выберите сотрудника"
                  label="Сотрудник"
                />
              ) : null}
              <NumberFormField
                _value={numberValue}
                _onChange={handleNumberChange}
                control={form.control}
                name="amount"
                label="Сумма"
              />
              <TextareaFormField
                control={form.control}
                name="comment"
                label="Комментарий"
              />

              <Button type="submit" disabled={isLoading}>
                Добавить платёж
              </Button>
            </AddForm>
          </DialogContent>

          {/*{ !hasShiftIsLoading && hasShiftData.has_shift ? (*/}
          {/*  <DialogContent>*/}
          {/*    <DialogHeader>*/}
          {/*      <DialogTitle>{dialogTitle}</DialogTitle>*/}
          {/*      <DialogDescription>{dialogDescription}</DialogDescription>*/}
          {/*    </DialogHeader>*/}

          {/*    <AddForm form={form} onSubmit={onSubmit} success={success} successDesc='Платёж успешно добавлен'>*/}
          {/*      <SelectFormField control={form.control} name="payment_method" placeholder="Выберите метод оплаты" label="Метод оплаты">*/}
          {/*        { data && Array.isArray(data) ? data.map((item) => (*/}
          {/*          <div key={item.id} className='mt-4 flex flex-col gap-2'>*/}
          {/*            <p className='ml-3 text-base font-semibold'>{item.name}</p>*/}
          {/*            <div className='text-sm'>*/}
          {/*              { item.payment_methods && Array.isArray(item.payment_methods) && item.payment_methods.map((item: any) => (*/}
          {/*                <SelectItem key={item.id} value={item.id.toString()}>{item.name}</SelectItem>*/}
          {/*              )) }*/}
          {/*            </div>*/}
          {/*          </div>*/}
          {/*        )) : (*/}
          {/*          <SelectItemSkeleton />*/}
          {/*        ) }*/}
          {/*      </SelectFormField>*/}
          {/*      <ReactSelectFormField*/}
          {/*        isValue*/}
          {/*        valueData={optionsData?.payment_types}*/}
          {/*        control={form.control}*/}
          {/*        name="payment_type"*/}
          {/*        placeholder="Выберите доход или расход" label="Доход / расход"*/}
          {/*      />*/}
          {/*      { outlay_type === 'WORKERS' ? (*/}
          {/*        <ReactSelectFormField*/}
          {/*          idData={workersData}*/}
          {/*          isLoading={workersLoading}*/}
          {/*          control={form.control}*/}
          {/*          name="worker"*/}
          {/*          placeholder="Выберите сотрудника"*/}
          {/*          label="Сотрудник"*/}
          {/*        />*/}
          {/*      ) : null }*/}
          {/*      <NumberFormField _value={numberValue} _onChange={handleNumberChange} control={form.control} name='amount' label='Сумма' />*/}
          {/*      <TextareaFormField control={form.control} name='comment' label='Комментарий' />*/}

          {/*      <Button type='submit' disabled={disabled}>*/}
          {/*        Добавить платёж*/}
          {/*      </Button>*/}
          {/*    </AddForm>*/}
          {/*  </DialogContent>*/}
          {/*) : (*/}
          {/*  <DialogContent>*/}
          {/*    <DialogHeader>*/}
          {/*      <DialogTitle>Откройте смену чтобы добавить продажу</DialogTitle>*/}
          {/*    </DialogHeader>*/}

          {/*    <Button disabled={openPending} onClick={() => createShift({})}>*/}
          {/*      <CalendarClock className="w-4 h-4 mr-2"/> Открыть смену*/}
          {/*    </Button>*/}
          {/*  </DialogContent>*/}
          {/*) }*/}
        </Dialog>
      ) : null}
    </>
  );
};

export default PaymentDialog;
