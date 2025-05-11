import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";
import useFilters from "@/hooks/useFilters.ts";
import useQueryString from "@/hooks/useQueryString.ts";
import { useState } from "react";
import { api } from "@/services/api.ts";
import OneChartWrapper from "@/components/others/OneChartWrapper.tsx";
import FiltersBlock from "@/components/others/FiltersBlock.tsx";
import { Bar, Line } from "react-chartjs-2";
import TableChartWrapper from "@/components/others/TableChartWrapper.tsx";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table.tsx";
import useNumberFormatter from "@/hooks/useNumberFormatter.ts";
import usePagination from "@/hooks/usePagination.ts";
import PaginationComponent from "@/components/others/PaginationComponent.tsx";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement,
  ArcElement
);

const barOptions = {
  responsive: true,
  indexAxis: "y" as const,
  elements: {
    bar: {
      borderWidth: 3,
    },
  },
};

const ClientsChartsSection = () => {
  const chartsFilterState = JSON.parse(
    localStorage.getItem("charts") ||
      JSON.stringify({
        currentPage: "",
        clientsPeriodTo: "",
        clientsPeriodFrom: "",
        clientsPeriodToFormatted: "",
        clientsPeriodFromFormatted: "",
      })
  );

  const { formatter } = useNumberFormatter();

  const { currentPage, setCurrentPage, totalPages, setTotalPages } =
    usePagination(chartsFilterState);
  const {
    periodTo: clientsPeriodTo,
    periodFrom: clientsPeriodFrom,
    periodFromFormatted: clientsPeriodFromFormatted,
    periodToFormatted: clientsPeriodToFormatted,
    setPeriodFrom: clientsSetPeriodFrom,
    setPeriodTo: clientsSetPeriodTo,
    client,
    setClient,
  } = useFilters(chartsFilterState);
  const {
    periodTo: tablePeriodTo,
    periodFrom: tablePeriodFrom,
    periodFromFormatted: tablePeriodFromFormatted,
    periodToFormatted: tablePeriodToFormatted,
    setPeriodFrom: tableSetPeriodFrom,
    setPeriodTo: tableSetPeriodTo,
    client: tableClient,
    setClient: setTableClient,
    orderField,
    setOrderField,
  } = useFilters(chartsFilterState);

  const {
    periodTo: clientLinearPeriodTo,
    periodFrom: clientLinearPeriodFrom,
    periodFromFormatted: clientLinearPeriodFromFormatted,
    periodToFormatted: clientLinearPeriodToFormatted,
    setPeriodFrom: clientLinearSetPeriodFrom,
    setPeriodTo: clientLinearSetPeriodTo,
    client: clientLinearClient,
    setClient: setLinearClient,
  } = useFilters(chartsFilterState);

  const clientsQueryParams: any = {
    start_date:
      clientsPeriodFromFormatted !== null ? clientsPeriodFromFormatted : "",
    end_date: clientsPeriodToFormatted !== null ? clientsPeriodToFormatted : "",
    client_id: client !== null ? client : "",
  };

  const clientsTableQueryParams: any = {
    page: currentPage,
    start_date:
      tablePeriodFromFormatted !== null ? tablePeriodFromFormatted : "",
    end_date: tablePeriodToFormatted !== null ? tablePeriodToFormatted : "",
    order_field: orderField !== null ? orderField : "total_orders_sum",
    client_id: tableClient !== null ? tableClient : "",
  };

  const { queryString: clientsQueryStringCollection } =
    useQueryString(clientsQueryParams);
  const { queryString: clientsTableQueryStringCollection } = useQueryString(
    clientsTableQueryParams
  );

  const [clientsQueryString, setClientsQueryString] = useState("");
  const [clientsTableQueryString, setClientsTableQueryString] = useState("");

  const { data: clientsData, isLoading: clientsLoading } =
    api.useGetAnalyticsQuery({
      queryString: clientsQueryString,
      item: "clients/chart",
    });
  const {
    data: clientsTableData,
    isLoading: clientsTableLoading,
    isFetching: clientsTableFetching,
  } = api.useGetAnalyticsQuery({
    queryString: clientsTableQueryString,
    item: "clients/top",
  });

  //Clinet params with Liner chart

  const [clientsLinerChartQueryString, setClientsLinerChartQueryString] =
    useState("");

  const clientsLinerChartQueryParams: any = {
    start_date:
      clientLinearPeriodFromFormatted !== null
        ? clientLinearPeriodFromFormatted
        : "",
    end_date:
      clientLinearPeriodToFormatted !== null
        ? clientLinearPeriodToFormatted
        : "",
    order_field: orderField !== null ? orderField : "total_orders_sum",
    client_id: clientLinearClient !== null ? clientLinearClient : "",
  };

  const { queryString: clientsLinerChartQueryStringCollection } =
    useQueryString(clientsLinerChartQueryParams);

  const { data: clientsLinerChartData, isLoading: clientsLinerChartLoading } =
    api.useGetAnalyticsQuery({
      queryString: clientsLinerChartQueryString,
      item: "clients/linear",
    });

  ///////////////////////////////

  if (clientsLoading || clientsLinerChartLoading || clientsTableLoading) {
    return <h3>Идет загрузка, подождите...</h3>;
  }

  const responsiveOptions = {
    responsive: true,
  };

  return (
    <>
      <TableChartWrapper>
        <div className="flex flex-col flex-1">
          <OneChartWrapper title="Клиенты">
            <FiltersBlock
              periodFrom={clientsPeriodFrom}
              periodTo={clientsPeriodTo}
              setPeriodFrom={clientsSetPeriodFrom}
              setPeriodTo={clientsSetPeriodTo}
              setClients={setClient}
              client={client}
              refetchData={() => {
                setClientsQueryString(clientsQueryStringCollection);
              }}
              pathName={"charts"}
              hasClients
              clientsNotMulti
            />
            {clientsData &&
            Array.isArray(clientsData?.chart?.labels) &&
            clientsData?.chart?.labels?.length !== 0 ? (
              <Bar data={clientsData?.chart} options={barOptions} />
            ) : (
              <p className="pt-10 pb-10 text-xl text-center font-medium text-neutral-400">
                Данные не найдены
              </p>
            )}
          </OneChartWrapper>

          <OneChartWrapper title="">
            <FiltersBlock
              periodFrom={clientLinearPeriodFrom}
              periodTo={clientLinearPeriodTo}
              setPeriodFrom={clientLinearSetPeriodFrom}
              setPeriodTo={clientLinearSetPeriodTo}
              setOrderField={setOrderField}
              orderField={orderField}
              setClients={setLinearClient}
              client={clientLinearClient}
              refetchData={() => {
                setClientsLinerChartQueryString(
                  clientsLinerChartQueryStringCollection
                );
              }}
              pathName={"linear"}
              hasClients
              hasOrderField
            />
            {clientsLinerChartData &&
            Array.isArray(clientsLinerChartData?.data?.labels) &&
            clientsLinerChartData?.data?.labels?.length !== 0 ? (
              <Line
                data={clientsLinerChartData?.data}
                options={responsiveOptions}
              />
            ) : (
              <p className="pt-10 pb-10 text-xl text-center font-medium text-neutral-400">
                Данные не найдены
              </p>
            )}
          </OneChartWrapper>
        </div>

        <div className="w-full flex flex-col flex-1 gap-3">
          <FiltersBlock
            periodFrom={tablePeriodFrom}
            periodTo={tablePeriodTo}
            setPeriodFrom={tableSetPeriodFrom}
            setPeriodTo={tableSetPeriodTo}
            setOrderField={setOrderField}
            setClients={setTableClient}
            client={tableClient}
            orderField={orderField}
            refetchData={() => {
              setClientsTableQueryString(clientsTableQueryStringCollection);
            }}
            pathName={"charts"}
            hasClients
            hasOrderField
            clientsNotMulti
          />

          <Table className="w-full">
            <TableHeader>
              <TableRow>
                <TableHead>№</TableHead>
                <TableHead>Имя</TableHead>
                <TableHead>Номер телефона</TableHead>
                <TableHead>Значение</TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {!clientsTableFetching &&
              clientsTableData &&
              Array.isArray(clientsTableData.results) ? (
                clientsTableData?.results?.map((item: any, index: number) => (
                  <TableRow key={index}>
                    <TableCell>{index + 1}</TableCell>
                    <TableCell>{item.full_name}</TableCell>
                    <TableCell>{item.phone_number || "-"}</TableCell>
                    <TableCell>
                      {formatter.format(item.aggregated_value)}{" "}
                      {orderField === "orders_count" ? "шт" : "сум"}
                    </TableCell>
                  </TableRow>
                ))
              ) : (
                <p>Загрузка...</p>
              )}
            </TableBody>
          </Table>

          <PaginationComponent
            data={clientsTableData}
            currentPage={currentPage}
            totalPages={totalPages}
            setCurrentPage={setCurrentPage}
            setTotalPages={setTotalPages}
            refetchData={() =>
              setClientsTableQueryString(clientsTableQueryStringCollection)
            }
          />
        </div>
      </TableChartWrapper>
    </>
  );
};

export default ClientsChartsSection;
