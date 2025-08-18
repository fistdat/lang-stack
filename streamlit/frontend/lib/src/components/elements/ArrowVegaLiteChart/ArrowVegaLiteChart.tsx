/**
 * Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022-2025)
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { FC, memo, useEffect, useLayoutEffect, useState } from "react"

import { Global } from "@emotion/react"
import { InsertChart, TableChart } from "@emotion-icons/material-outlined"

import { ElementFullscreenContext } from "~lib/components/shared/ElementFullscreen/ElementFullscreenContext"
import { withFullScreenWrapper } from "~lib/components/shared/FullScreenWrapper"
import Toolbar, {
  StyledToolbarElementContainer,
  ToolbarAction,
} from "~lib/components/shared/Toolbar"
import { ReadOnlyGrid } from "~lib/components/widgets/DataFrame"
import { useCalculatedDimensions } from "~lib/hooks/useCalculatedDimensions"
import { useRequiredContext } from "~lib/hooks/useRequiredContext"
import { WidgetStateManager } from "~lib/WidgetStateManager"

import { VegaLiteChartElement } from "./arrowUtils"
import {
  StyledVegaLiteChartContainer,
  StyledVegaLiteChartTooltips,
} from "./styled-components"
import { useVegaElementPreprocessor } from "./useVegaElementPreprocessor"
import { useVegaEmbed } from "./useVegaEmbed"

function isFacetChart(spec: string | object): boolean {
  try {
    const parsedSpec = typeof spec === "string" ? JSON.parse(spec) : spec

    return !!(
      parsedSpec.facet ||
      // TODO (lawilby): do some tests for row/column
      // shorthand facet charts to confirm they work with
      // sizing in the same way.
      parsedSpec.encoding?.row ||
      parsedSpec.encoding?.column ||
      parsedSpec.encoding?.facet
    )
  } catch {
    return false
  }
}
export interface Props {
  element: VegaLiteChartElement
  widgetMgr: WidgetStateManager
  fragmentId?: string
  disableFullscreenMode?: boolean
}

const ArrowVegaLiteChart: FC<Props> = ({
  disableFullscreenMode,
  element: inputElement,
  fragmentId,
  widgetMgr,
}) => {
  const [showData, setShowData] = useState(false)
  const [enableShowData, setEnableShowData] = useState(false)

  const {
    expanded: isFullScreen,
    height: fullScreenHeight,
    width: fullScreenWidth,
    expand,
    collapse,
  } = useRequiredContext(ElementFullscreenContext)

  // When we are in full screen mode, this will be the
  // width/height of the screen based on the expansion
  // of the parent StyledFullScreenFrame.
  // Otherwise, it will be according to the user's settings
  // determined by styling on the StyledElementContainer.
  const {
    width: containerWidth,
    height: containerHeight,
    elementRef: containerRef,
  } = useCalculatedDimensions(
    // We need to update whenever the showData state changes because
    // the underlying element ref that needs to be observed is updated.
    [showData],
    // Use 0 as fallback instead of -1 because Vega-Lite cannot handle negative dimensions
    0
  )

  // Facet charts need the container element to have a width and also
  // do not work well with stretch/container width
  // so they cannot use the width from the StyledVegaLiteChartContainer.
  const isFacet = isFacetChart(inputElement.spec)

  // We preprocess the input vega element to do a two things:
  // 1. Update the spec to handle Streamlit specific configurations such as
  //    theming, container width, and full screen mode
  // 2. Stabilize some aspects of the input element to detect changes in the
  //    configuration of the chart since each element will always provide new references
  //    Note: We do not stabilize data/datasets as that is managed by the embed.
  const element = useVegaElementPreprocessor(
    inputElement,
    isFullScreen,
    // Facet charts enter a loop when using the width/height from the StyledVegaLiteChartContainer.
    // The fullscreen wrapper dimensions will be based on the element container when not in full screen mode.
    isFacet ? (fullScreenWidth ?? 0) : containerWidth,
    fullScreenHeight ?? 0
  )

  // This hook provides lifecycle functions for creating and removing the view.
  // It also will update the view if the data changes (and not the spec)
  const { createView, updateView, finalizeView } = useVegaEmbed(
    element,
    widgetMgr,
    fragmentId
  )

  const { data, datasets, spec } = element

  // Create the view once the container is ready and re-create
  // if the spec changes or the dimensions change.
  // We utilize useLayoutEffect to ensure that the view is created
  // after the container is mounted to avoid layout shift.
  useLayoutEffect(() => {
    if (containerRef.current !== null) {
      // eslint-disable-next-line @typescript-eslint/no-floating-promises -- TODO: Fix this
      createView(containerRef, spec)
    }

    return finalizeView
    // We can't use width in this dependency array because it causes facet charts to enter a loop.
    // TODO(lawilby): Do we need width/height in this dependency array? It seems any changes
    // Are the changes in the spec enough?
  }, [
    createView,
    finalizeView,
    spec,
    fullScreenWidth,
    fullScreenHeight,
    showData,
    containerRef,
  ])

  // The references to data and datasets will always change each rerun
  // because the forward message always produces new references, so
  // this function will run regularly to update the view.
  useEffect(() => {
    // eslint-disable-next-line @typescript-eslint/no-floating-promises -- TODO: Fix this
    updateView(data, datasets)
  }, [data, datasets, updateView])

  useEffect(() => {
    // We only show data if its provided via data or if there
    // is one data set in the datasets array. In this case,
    // only the first dataset is shown:
    if (data || (datasets && datasets[0]?.data)) {
      setEnableShowData(true)
    } else {
      setEnableShowData(false)
    }
  }, [data, datasets])

  if (showData) {
    return (
      <ReadOnlyGrid
        data={data ?? datasets[0]?.data}
        height={fullScreenHeight ?? containerHeight ?? undefined}
        customToolbarActions={[
          <ToolbarAction
            key="show-chart"
            label="Show chart"
            icon={InsertChart}
            onClick={() => {
              setShowData(false)
            }}
          />,
        ]}
      />
    )
  }

  // Create the container inside which Vega draws its content.
  // To style the Vega tooltip, we need to apply global styles since
  // the tooltip element is drawn outside of this component.
  return (
    <StyledToolbarElementContainer
      height={fullScreenHeight}
      useContainerWidth={element.useContainerWidth}
    >
      <Toolbar
        target={StyledToolbarElementContainer}
        isFullScreen={isFullScreen}
        onExpand={expand}
        onCollapse={collapse}
        disableFullscreenMode={disableFullscreenMode}
      >
        {enableShowData && (
          <ToolbarAction
            label="Show data"
            icon={TableChart}
            onClick={() => {
              setShowData(true)
            }}
          />
        )}
      </Toolbar>
      <Global styles={StyledVegaLiteChartTooltips} />
      <StyledVegaLiteChartContainer
        data-testid="stVegaLiteChart"
        className="stVegaLiteChart"
        useContainerWidth={element.useContainerWidth}
        isFullScreen={isFullScreen}
        ref={containerRef}
      />
    </StyledToolbarElementContainer>
  )
}

const ArrowVegaLiteChartWithFullScreen =
  withFullScreenWrapper(ArrowVegaLiteChart)
export default memo(ArrowVegaLiteChartWithFullScreen)
