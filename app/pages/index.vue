<script setup lang="ts">
const { t } = useSite()
useSiteSeo()
</script>

<template>
  <div>
    <a class="skip-link" href="#main">{{ t.skip }}</a>
    <SiteHeader />
    <main id="main">
      <HeroSection />
      <MarqueeStrip />
      <AboutSection />
      <AiSection />
      <ServicesSection />
      <WorkSection />
      <LabSection />
      <ProcessSection />
      <FaqSection />
      <ContactSection />
    </main>
    <SiteFooter />
    <ClientOnly><GeoLangHint /></ClientOnly>
    <DesignModal />
  </div>
</template>
